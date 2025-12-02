from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from data.mock_data import get_student_data
from factories.challenge_factory import ChallengeFactory
from cognitive_module.cognitive_endpoints import register_cognitive_routes


app = Flask(__name__)
CORS(app)  # Habilitar CORS para integração com Inven!RA
register_cognitive_routes(app)

# ========================================
# PÁGINA INICIAL
# ========================================
@app.route("/")
def index():
    """Página inicial do Activity Provider"""
    return jsonify({
        'message': 'Dia & Noite: O Mundo dos Animais - Activity Provider',
        'status': 'online',
        'version': '1.0.0',
        'autores': ['Henrique Crachat (2501450)', 'Fábio Amado (2501444)'],
        'endpoints': {
            'config': '/config',
            'params': '/api/params',
            'deploy': '/api/deploy (POST)',
            'analyticsList': '/api/analytics-list',
            'analytics': '/api/analytics (POST)',
            # Endpoints do Módulo Cognitivo
            'cognitive_challenge': '/api/cognitive/challenge (POST)',            
            'cognitive_submit': '/api/cognitive/submit-answer (POST)',            
            'cognitive_accuracy': '/api/cognitive/accuracy/{user_id} (GET)',            
            'cognitive_progress': '/api/cognitive/progress/{user_id} (GET)',            
            'cognitive_recommendations': '/api/cognitive/recommendations/{user_id} (GET)'
        }
    })


# ========================================
# ENDPOINT 1: Página de Configuração
# ========================================
@app.route("/config")
def config():
    """Renderiza página HTML de configuração"""
    return render_template('config.html')


# ========================================
# ENDPOINT 2: Parâmetros JSON
# ========================================
@app.route("/api/params", methods=['GET'])
def params():
    """Retorna parâmetros configuráveis da atividade"""
    return jsonify([
        {"name": "idioma", "type": "text/plain"},
        {"name": "nivelInicial", "type": "integer"},
        {"name": "tempoSessaoMinimo", "type": "integer"},
        {"name": "objetivoAcertos", "type": "integer"},
        {"name": "modulosAtivos", "type": "text/plain"}
    ])


# ========================================
# ENDPOINT 3: Deploy da Atividade
# ========================================
@app.route("/api/deploy", methods=['POST'])
def deploy():
    """Recebe configuração e retorna URL da atividade para o aluno"""
    data = request.get_json()
    
    # Validar dados obrigatórios
    if not data or 'inveniraStdID' not in data:
        return jsonify({
            'error': 'inveniraStdID é obrigatório'
        }), 400
    
    # Extrair parâmetros (com valores padrão)
    invenira_std_id = data.get('inveniraStdID')
    idioma = data.get('idioma', 'pt')
    nivel_inicial = data.get('nivelInicial', 1)
    tempo_sessao_minimo = data.get('tempoSessaoMinimo', 5)
    objetivo_acertos = data.get('objetivoAcertos', 80)
    modulos_ativos = data.get('modulosAtivos', 'cognitivo,sessoes')
    
    # Construir URL da atividade
    activity_url = f"{request.scheme}://{request.host}/activity?student={invenira_std_id}&lang={idioma}&level={nivel_inicial}"
    
    return jsonify({
        'success': True,
        'activityUrl': activity_url,
        'config': {
            'idioma': idioma,
            'nivelInicial': nivel_inicial,
            'tempoSessaoMinimo': tempo_sessao_minimo,
            'objetivoAcertos': objetivo_acertos,
            'modulosAtivos': modulos_ativos
        }
    })


# ========================================
# ENDPOINT 4: Lista de Analytics Disponíveis
# ========================================
@app.route("/api/analytics-list", methods=['GET'])
def analytics_list():
    """Retorna lista de todos os analytics disponíveis"""
    return jsonify({
        "quantAnalytics": [
            # Módulo Henrique (Cognitivo)
            {"name": "Total de Respostas", "type": "integer"},
            {"name": "Respostas Corretas", "type": "integer"},
            {"name": "Respostas Incorretas", "type": "integer"},
            {"name": "Taxa de Acerto (%)", "type": "integer"},
            {"name": "Nível Atual", "type": "integer"},
            {"name": "Animais Descobertos", "type": "integer"},
            {"name": "Categorias Completadas", "type": "integer"},
            
            # Módulo Fábio (Sessões)
            {"name": "Total de Sessões", "type": "integer"},
            {"name": "Tempo Total de Jogo (min)", "type": "integer"},
            {"name": "Tempo Médio por Sessão (min)", "type": "integer"},
            {"name": "Interações Totais", "type": "integer"},
            {"name": "Repetições de Níveis", "type": "integer"},
            {"name": "Dias Consecutivos", "type": "integer"}
        ],
        "qualAnalytics": [
            {"name": "Detalhes de Respostas", "type": "URL"},
            {"name": "Progresso por Categoria", "type": "URL"},
            {"name": "Histórico de Sessões", "type": "URL"},
            {"name": "Padrão de Utilização", "type": "URL"}
        ]
    })


# ========================================
# ENDPOINT 5: Dados de Analytics
# ========================================
@app.route("/api/analytics", methods=['POST'])
def analytics():
    """Retorna analytics de um aluno específico"""
    data = request.get_json()
    
    # Validar dados obrigatórios
    if not data or 'inveniraStdID' not in data:
        return jsonify({
            'error': 'inveniraStdID é obrigatório'
        }), 400
    
    invenira_std_id = data.get('inveniraStdID')
    student_data = get_student_data(invenira_std_id)
    base_url = f"{request.scheme}://{request.host}"
    
    return jsonify({
        "inveniraStdID": invenira_std_id,
        "quantAnalytics": [
            # Módulo Henrique (Cognitivo)
            {
                "name": "Total de Respostas",
                "type": "integer",
                "value": student_data['totalRespostas']
            },
            {
                "name": "Respostas Corretas",
                "type": "integer",
                "value": student_data['respostasCorretas']
            },
            {
                "name": "Respostas Incorretas",
                "type": "integer",
                "value": student_data['respostasIncorretas']
            },
            {
                "name": "Taxa de Acerto (%)",
                "type": "integer",
                "value": student_data['taxaAcerto']
            },
            {
                "name": "Nível Atual",
                "type": "integer",
                "value": student_data['nivelAtual']
            },
            {
                "name": "Animais Descobertos",
                "type": "integer",
                "value": student_data['animaisDescobertos']
            },
            {
                "name": "Categorias Completadas",
                "type": "integer",
                "value": student_data['categoriasCompletadas']
            },
            
            # Módulo Fábio (Sessões)
            {
                "name": "Total de Sessões",
                "type": "integer",
                "value": student_data['totalSessoes']
            },
            {
                "name": "Tempo Total de Jogo (min)",
                "type": "integer",
                "value": student_data['tempoTotalJogo']
            },
            {
                "name": "Tempo Médio por Sessão (min)",
                "type": "integer",
                "value": student_data['tempoMedioSessao']
            },
            {
                "name": "Interações Totais",
                "type": "integer",
                "value": student_data['interacoesTotais']
            },
            {
                "name": "Repetições de Níveis",
                "type": "integer",
                "value": student_data['repeticoesNiveis']
            },
            {
                "name": "Dias Consecutivos",
                "type": "integer",
                "value": student_data['diasConsecutivos']
            }
        ],
        "qualAnalytics": [
            {
                "name": "Detalhes de Respostas",
                "type": "URL",
                "value": f"{base_url}/details/{invenira_std_id}"
            },
            {
                "name": "Progresso por Categoria",
                "type": "URL",
                "value": f"{base_url}/progress/{invenira_std_id}"
            },
            {
                "name": "Histórico de Sessões",
                "type": "URL",
                "value": f"{base_url}/sessions/{invenira_std_id}"
            },
            {
                "name": "Padrão de Utilização",
                "type": "URL",
                "value": f"{base_url}/usage/{invenira_std_id}"
            }
        ]
    })


@app.route("/api/game/get-challenge", methods=['POST'])
def get_challenge():
    """
    Endpoint que usa o Factory Method para criar desafios.
    
    Body:
    {
        "animal_id": 1,
        "challenge_type": "audio",  // ou "random"
        "difficulty": 2
    }
    """
    data = request.get_json()
    
    animal_id = data.get('animal_id', 1)
    challenge_type = data.get('challenge_type', 'random')
    difficulty = data.get('difficulty', 1)
    
    try:
        # USO DO FACTORY METHOD
        if challenge_type == 'random':
            challenge = ChallengeFactory.create_random_challenge(animal_id, difficulty)
        else:
            challenge = ChallengeFactory.create_challenge(challenge_type, animal_id, difficulty)
        
        return jsonify({
            'success': True,
            'challenge': challenge.to_dict()
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route("/api/game/validate-answer", methods=['POST'])
def validate_answer():
    """
    Validar resposta de um desafio.
    
    Body:
    {
        "challenge_id": "audio_1_1234",
        "answer": "Leão",
        "animal_id": 1,
        "challenge_type": "audio"
    }
    """
    data = request.get_json()
    
    # Recriar o desafio usando o Factory
    challenge = ChallengeFactory.create_challenge(
        data['challenge_type'],
        data['animal_id']
    )
    
    is_correct = challenge.validate_answer(data['answer'])
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': challenge.correct_answer if not is_correct else None
    })

# ========================================
# ROTA TEMPORÁRIA: Atividade (mockup)
# ========================================
@app.route("/activity")
def activity():
    """Página mockup da atividade (não implementada nesta semana)"""
    student = request.args.get('student', 'desconhecido')
    lang = request.args.get('lang', 'pt')
    level = request.args.get('level', '1')
    
    return render_template('index.html')  # Usar o index.html existente por enquanto


# ========================================
# INICIALIZAÇÃO
# ========================================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

