"""
Endpoints Flask para Módulo Cognitivo - Henrique Crachat (2501450)

Integra múltiplos padrões de design:
- Factory Method (ChallengeFactory) - Criação de desafios
- Observer (Observers) - Notificação de eventos
- Decorator (TimedDecorator) - Funcionalidades opcionais

Padrão Observer: Quando um desafio é criado ou completado, múltiplos
observers são notificados automaticamente sem acoplamento direto.

Autor: Henrique Crachat (2501450@estudante.uab.pt)
"""
from flask import request, jsonify
from factories.challenge_factory import ChallengeFactory
from cognitive_module.cognitive_analytics import cognitive_analytics

import time


# =====================================================
# OBSERVERS GLOBAIS (Padrão Observer)
# =====================================================
# Nota: Observers são inicializados dentro de register_cognitive_routes()
# para evitar importação circular
analytics_observer = None
achievement_observer = None
invenira_observer = None
level_progression_observer = None


# =====================================================
# HELPER FUNCTIONS (Padrão Observer)
# =====================================================

def attach_observers_to_challenge(challenge):
    """
    Anexa todos os observers a um desafio.

    Padrão Observer: Esta função centraliza o registro de observers,
    permitindo fácil adição/remoção de observers sem modificar
    a lógica dos endpoints.

    Args:
        challenge: Instância de Challenge para anexar observers

    Returns:
        Challenge com observers anexados
    """
    challenge.attach(analytics_observer)
    challenge.attach(achievement_observer)
    challenge.attach(invenira_observer)
    challenge.attach(level_progression_observer)
    return challenge


# =====================================================
# ENDPOINTS DO MÓDULO COGNITIVO (HENRIQUE)
# =====================================================


def register_cognitive_routes(app):
    """
    Registar rotas do módulo cognitivo no Flask app.

    Args:
        app: Instância Flask
    """

    # =====================================================
    # INICIALIZAR OBSERVERS (Padrão Observer)
    # =====================================================
    # Import aqui para evitar importação circular
    from observers.analytics_observer import AnalyticsObserver
    from observers.achievement_observer import AchievementObserver
    from observers.invenira_observer import InveniraObserver
    from observers.level_progression_observer import LevelProgressionObserver

    global analytics_observer, achievement_observer, invenira_observer, level_progression_observer

    # Criar instâncias dos observers
    analytics_observer = AnalyticsObserver(cognitive_analytics)
    achievement_observer = AchievementObserver()
    invenira_observer = InveniraObserver()
    level_progression_observer = LevelProgressionObserver(invenira_observer=invenira_observer)

    @app.route("/api/cognitive/challenge", methods=['POST'])
    def create_cognitive_challenge():
        """
        Cria desafio com tracking cognitivo.

        PADRÕES INTEGRADOS:
        - Factory Method: Cria instância de Challenge
        - Observer: Anexa observers e notifica início do desafio

        Body:
        {
            "user_id": "student123",
            "animal_id": 1,
            "challenge_type": "audio"  // ou "random"
        }

        Returns:
            Challenge + contexto cognitivo
        """
        data = request.get_json()

        if not data or 'user_id' not in data or 'animal_id' not in data:
            return jsonify({
                'success': False,
                'error': 'user_id e animal_id são obrigatórios'
            }), 400

        user_id = data['user_id']
        animal_id = data['animal_id']
        challenge_type = data.get('challenge_type', 'random')

        try:
            # 1. FACTORY METHOD: Criar desafio
            if challenge_type == 'random':
                challenge = ChallengeFactory.create_random_challenge(animal_id)
            else:
                challenge = ChallengeFactory.create_challenge(challenge_type, animal_id)

            # 2. OBSERVER: Anexar observers ao desafio
            attach_observers_to_challenge(challenge)

            # 3. OBSERVER: Notificar que desafio foi iniciado
            challenge.notify_started(user_id)

            # Obter recomendações baseadas em performance
            recommended_types = cognitive_analytics.get_recommended_challenges(user_id)

            # Obter progresso do utilizador (via observers)
            level_progress = level_progression_observer.get_user_progress(user_id)

            return jsonify({
                'success': True,
                'challenge': challenge.to_dict(),
                'cognitive_context': {
                    'user_level': level_progress['current_level']['number'],
                    'level_name': level_progress['current_level']['name'],
                    'xp': level_progress['xp']['current'],
                    'recommended_types': recommended_types,
                    'animals_discovered': len(cognitive_analytics.user_data.get(user_id, {}).get('animals_discovered', []))
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route("/api/cognitive/submit-answer", methods=['POST'])
    def submit_cognitive_answer():
        """
        Submete resposta com tracking cognitivo completo.

        PADRÕES INTEGRADOS:
        - Factory Method: Recria Challenge para validação
        - Observer: Notifica todos observers sobre conclusão do desafio

        Quando a resposta é submetida, TODOS os observers são notificados:
        - AnalyticsObserver: Atualiza estatísticas cognitivas
        - AchievementObserver: Verifica conquistas desbloqueadas
        - InveniraObserver: Notifica plataforma externa
        - LevelProgressionObserver: Atualiza XP e nível

        Body:
        {
            "user_id": "student123",
            "challenge_type": "audio",
            "animal_id": 1,
            "answer": "Leão",
            "time_taken": 12.5
        }

        Returns:
            Validação + analytics + achievements + level progress
        """
        data = request.get_json()

        required = ['user_id', 'challenge_type', 'animal_id', 'answer']
        if not all(field in data for field in required):
            return jsonify({
                'success': False,
                'error': f'Campos obrigatórios: {required}'
            }), 400

        try:
            # 1. FACTORY METHOD: Recriar challenge
            challenge = ChallengeFactory.create_challenge(
                data['challenge_type'],
                data['animal_id']
            )

            # 2. OBSERVER: Anexar observers
            attach_observers_to_challenge(challenge)

            # 3. Validar resposta
            user_id = data['user_id']
            answer = data['answer']
            time_taken = data.get('time_taken', 0)
            is_correct = challenge.validate_answer(answer)

            # 4. OBSERVER: Notificar TODOS observers sobre conclusão
            # Esta linha dispara todas as atualizações automaticamente!
            challenge.notify_completed(user_id, answer, time_taken, is_correct)

            # 5. Coletar dados de todos os observers para resposta
            # Analytics
            analytics_progress = analytics_observer.get_user_progress(user_id)

            # Achievements
            user_achievements = achievement_observer.get_user_achievements(user_id)

            # Level Progression
            level_progress = level_progression_observer.get_user_progress(user_id)

            return jsonify({
                'success': True,
                'result': {
                    'is_correct': is_correct,
                    'correct_answer': challenge.correct_answer if not is_correct else None,
                    'time_taken': time_taken
                },
                'analytics': {
                    'accuracy_rate': analytics_progress['summary']['accuracy_rate'],
                    'total_challenges': analytics_progress['summary']['total_challenges'],
                    'current_level': analytics_progress['summary']['current_level']
                },
                'level_progression': {
                    'current_level': level_progress['current_level'],
                    'xp': level_progress['xp'],
                    'next_level': level_progress['next_level']
                },
                'achievements': {
                    'unlocked_count': user_achievements['unlocked_count'],
                    'completion_percentage': user_achievements['completion_percentage'],
                    'recently_unlocked': user_achievements['unlocked'][-3:] if user_achievements['unlocked'] else []
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route("/api/cognitive/accuracy/<user_id>", methods=['GET'])
    def get_accuracy(user_id):
        """
        Retorna taxa de acerto do aluno.
        
        Query params:
            ?type=audio  (opcional: filtrar por tipo)
        
        Example:
            GET /api/cognitive/accuracy/student123
            GET /api/cognitive/accuracy/student123?type=audio
        """
        challenge_type = request.args.get('type')
        
        try:
            accuracy_data = cognitive_analytics.get_accuracy_by_type(
                user_id,
                challenge_type
            )
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'accuracy': accuracy_data
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route("/api/cognitive/progress/<user_id>", methods=['GET'])
    def get_progress(user_id):
        """
        Retorna relatório completo de progresso cognitivo.
        
        Example:
            GET /api/cognitive/progress/student123
        """
        try:
            report = cognitive_analytics.get_progress_report(user_id)
            
            return jsonify({
                'success': True,
                'report': report
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route("/api/analytics", methods=['POST'])
    def get_cognitive_analytics():
        """
        Endpoint compatível com Inven!RA para analytics cognitivos.
        
        Body:
        {
            "studentId": "student123"
        }
        
        Returns:
            Analytics formatados para Inven!RA
        """
        data = request.get_json()
        
        if not data or 'studentId' not in data:
            return jsonify({
                'success': False,
                'error': 'studentId é obrigatório'
            }), 400
        
        try:
            analytics = cognitive_analytics.export_analytics(data['studentId'])
            
            return jsonify({
                'success': True,
                'analytics': analytics
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route("/api/cognitive/recommendations/<user_id>", methods=['GET'])
    def get_recommendations(user_id):
        """
        Retorna tipos de desafios recomendados baseado em performance.
        
        Example:
            GET /api/cognitive/recommendations/student123
        """
        try:
            recommended = cognitive_analytics.get_recommended_challenges(user_id)
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'recommended_types': recommended,
                'available_types': ChallengeFactory.get_available_types()
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


# =====================================================
# INSTRUÇÕES DE INTEGRAÇÃO
# =====================================================
"""
Para integrar no App.py:

1. Importar no início:
   from cognitive_module.cognitive_endpoints import register_cognitive_routes

2. Depois de criar app, adicionar:
   register_cognitive_routes(app)

3. Testar endpoints:
   
   # Criar desafio com tracking cognitivo
   curl -X POST http://localhost:5000/api/cognitive/challenge \
     -H "Content-Type: application/json" \
     -d '{"user_id": "student123", "animal_id": 1, "challenge_type": "audio"}'
   
   # Submeter resposta
   curl -X POST http://localhost:5000/api/cognitive/submit-answer \
     -H "Content-Type: application/json" \
     -d '{"user_id": "student123", "challenge_type": "audio", "animal_id": 1, "answer": "Leão", "time_taken": 10}'
   
   # Ver accuracy
   curl http://localhost:5000/api/cognitive/accuracy/student123
   
   # Ver progresso
   curl http://localhost:5000/api/cognitive/progress/student123
"""
