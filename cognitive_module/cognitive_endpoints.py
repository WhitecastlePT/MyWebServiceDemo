"""
Endpoints Flask para Módulo Cognitivo - Henrique Crachat (2501450)

Integra múltiplos padrões de design:
- Factory Method (ChallengeFactory) - Criação de desafios
- Observer (Observers) - Notificação de eventos
- Decorator (TimedDecorator) - Funcionalidades opcionais

Padrão Observer: Quando um desafio é criado ou completado, múltiplos
observers são notificados automaticamente sem acoplamento direto.

ANTI-PADRÃO CORRIGIDO: Singleton Abuse / Global State
Anteriormente, observers eram variáveis globais. Agora usam Dependency Injection
via ObserversContainer, permitindo testes isolados e multi-tenancy.

Autor: Henrique Crachat (2501450@estudante.uab.pt)
"""
from flask import request, jsonify
from factories.challenge_factory import ChallengeFactory
from cognitive_module.observers_container import ObserversContainer

import time


# =====================================================
# ENDPOINTS DO MÓDULO COGNITIVO (HENRIQUE)
# =====================================================


def register_cognitive_routes(app, observers_container=None):
    """
    Registar rotas do módulo cognitivo no Flask app.

    DEPENDENCY INJECTION: Aceita observers_container como parâmetro opcional.
    Se None, cria uma nova instância. Permite injetar mock containers para testes.

    Args:
        app: Instância Flask
        observers_container: ObserversContainer opcional (para DI/testes)
    """

    # =====================================================
    # DEPENDENCY INJECTION (Anti-padrão corrigido)
    # =====================================================
    # Criar container se não fornecido (padrão de produção)
    if observers_container is None:
        observers_container = ObserversContainer()

    # Usar closure para capturar observers_container nos endpoints
    observers = observers_container
    cognitive_analytics = observers.cognitive_analytics

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

            # 2. OBSERVER: Anexar observers ao desafio (via container)
            observers.attach_all_to_challenge(challenge)

            # 3. OBSERVER: Notificar que desafio foi iniciado
            challenge.notify_started(user_id)

            # Obter recomendações baseadas em performance
            recommended_types = cognitive_analytics.get_recommended_challenges(user_id)

            # Obter progresso do utilizador (via observers)
            level_progress = observers.level_progression_observer.get_user_progress(user_id)

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

            # 2. OBSERVER: Anexar observers (via container)
            observers.attach_all_to_challenge(challenge)

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
            analytics_progress = observers.analytics_observer.get_user_progress(user_id)

            # Achievements
            user_achievements = observers.achievement_observer.get_user_achievements(user_id)

            # Level Progression
            level_progress = observers.level_progression_observer.get_user_progress(user_id)

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
