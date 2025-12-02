"""
Endpoints Flask para Módulo Cognitivo - Henrique Crachat (2501450)

Integra Factory Method (ChallengeFactory) com Cognitive Analytics.

Autor: Henrique Crachat (2501450@estudante.uab.pt)
"""
from flask import request, jsonify
from factories.challenge_factory import ChallengeFactory
from cognitive_module.cognitive_analytics import cognitive_analytics
import time


# =====================================================
# ENDPOINTS DO MÓDULO COGNITIVO (HENRIQUE)
# =====================================================
# Adicionar estas rotas ao App.py existente
# =====================================================


def register_cognitive_routes(app):
    """
    Registar rotas do módulo cognitivo no Flask app.
    
    Args:
        app: Instância Flask
    """
    
    @app.route("/api/cognitive/challenge", methods=['POST'])
    def create_cognitive_challenge():
        """
        Cria desafio com tracking cognitivo.
        
        INTEGRAÇÃO FACTORY METHOD:
        - Usa ChallengeFactory.create_challenge()
        - Retorna Challenge para o aluno
        - Prepara para tracking de resposta
        
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
            # USAR FACTORY METHOD para criar desafio
            if challenge_type == 'random':
                challenge = ChallengeFactory.create_random_challenge(animal_id)
            else:
                challenge = ChallengeFactory.create_challenge(challenge_type, animal_id)
            
            # Obter recomendações baseadas em performance
            recommended_types = cognitive_analytics.get_recommended_challenges(user_id)
            
            return jsonify({
                'success': True,
                'challenge': challenge.to_dict(),
                'cognitive_context': {
                    'user_level': cognitive_analytics.user_data.get(user_id, {}).get('current_level', 1),
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
        
        INTEGRAÇÃO FACTORY METHOD:
        - Recria Challenge usando Factory
        - Usa challenge.validate_answer() para validar
        - Regista analytics cognitivos
        
        Body:
        {
            "user_id": "student123",
            "challenge_type": "audio",
            "animal_id": 1,
            "answer": "Leão",
            "time_taken": 12.5
        }
        
        Returns:
            Validação + analytics atualizados
        """
        data = request.get_json()
        
        required = ['user_id', 'challenge_type', 'animal_id', 'answer']
        if not all(field in data for field in required):
            return jsonify({
                'success': False,
                'error': f'Campos obrigatórios: {required}'
            }), 400
        
        try:
            # Recriar challenge usando FACTORY METHOD
            challenge = ChallengeFactory.create_challenge(
                data['challenge_type'],
                data['animal_id']
            )
            
            # Registar resposta com analytics cognitivo
            result = cognitive_analytics.record_response(
                user_id=data['user_id'],
                challenge=challenge,
                answer=data['answer'],
                time_taken=data.get('time_taken', 0)
            )
            
            return jsonify({
                'success': True,
                **result
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
