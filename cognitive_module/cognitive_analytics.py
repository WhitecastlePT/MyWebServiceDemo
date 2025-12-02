"""
Módulo de Analytics Cognitivo - Henrique Crachat (2501450)

Integração do padrão Factory Method com tracking cognitivo.
Responsável por monitorizar:
- Respostas corretas/incorretas
- Taxa de acerto por tipo de desafio
- Níveis de dificuldade
- Animais descobertos
- Performance por categoria

Autor: Henrique Crachat (2501450@estudante.uab.pt)
"""
from typing import Dict, List, Optional
from datetime import datetime
from models.challenge import Challenge


class CognitiveAnalytics:
    """
    Sistema de Analytics Cognitivo.
    
    Usa o Factory Method (ChallengeFactory) para obter desafios
    e monitoriza o desempenho cognitivo do aluno.
    """
    
    def __init__(self):
        """Inicializa o sistema de analytics"""
        # Estrutura: {user_id: {dados}}
        self.user_data: Dict[str, Dict] = {}
    
    def initialize_user(self, user_id: str) -> None:
        """
        Inicializa dados de um novo utilizador.
        
        Args:
            user_id: ID único do utilizador
        """
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'total_challenges': 0,
                'correct_answers': 0,
                'incorrect_answers': 0,
                'accuracy_rate': 0.0,
                'by_type': {
                    'audio': {'total': 0, 'correct': 0, 'accuracy': 0.0},
                    'visual': {'total': 0, 'correct': 0, 'accuracy': 0.0},
                    'habitat': {'total': 0, 'correct': 0, 'accuracy': 0.0},
                    'classification': {'total': 0, 'correct': 0, 'accuracy': 0.0}
                },
                'animals_discovered': [],
                'current_level': 1,
                'categories_completed': [],
                'first_attempt': datetime.now().isoformat(),
                'last_attempt': datetime.now().isoformat()
            }
    
    def record_response(self, user_id: str, challenge: Challenge, 
                       answer: str, time_taken: float) -> Dict:
        """
        Regista uma resposta a um desafio.
        
        Integração com Factory Method:
        - Recebe instância de Challenge criada pelo Factory
        - Extrai tipo do desafio via challenge.get_challenge_type()
        - Valida resposta via challenge.validate_answer()
        
        Args:
            user_id: ID do utilizador
            challenge: Instância de Challenge (do Factory)
            answer: Resposta do aluno
            time_taken: Tempo em segundos
        
        Returns:
            Dicionário com resultado e analytics atualizados
        """
        self.initialize_user(user_id)
        
        # Validar resposta usando método da Challenge
        is_correct = challenge.validate_answer(answer)
        challenge_type = challenge.get_challenge_type()
        
        # Atualizar estatísticas globais
        user = self.user_data[user_id]
        user['total_challenges'] += 1
        
        if is_correct:
            user['correct_answers'] += 1
        else:
            user['incorrect_answers'] += 1
        
        # Atualizar taxa de acerto global
        user['accuracy_rate'] = (
            user['correct_answers'] / user['total_challenges'] * 100
        )
        
        # Atualizar estatísticas por tipo
        type_stats = user['by_type'][challenge_type]
        type_stats['total'] += 1
        if is_correct:
            type_stats['correct'] += 1
        type_stats['accuracy'] = (
            type_stats['correct'] / type_stats['total'] * 100
        )
        
        # Registar animal descoberto
        if is_correct and challenge.animal_id not in user['animals_discovered']:
            user['animals_discovered'].append(challenge.animal_id)
        
        # Atualizar último acesso
        user['last_attempt'] = datetime.now().isoformat()
        
        # Calcular nível baseado em desempenho
        user['current_level'] = self._calculate_level(user)
        
        return {
            'is_correct': is_correct,
            'correct_answer': challenge.correct_answer if not is_correct else None,
            'time_taken': time_taken,
            'points_earned': self._calculate_points(is_correct, time_taken),
            'current_accuracy': user['accuracy_rate'],
            'type_accuracy': type_stats['accuracy'],
            'current_level': user['current_level'],
            'animals_discovered': len(user['animals_discovered'])
        }
    
    def get_accuracy_by_type(self, user_id: str, 
                            challenge_type: Optional[str] = None) -> Dict:
        """
        Retorna taxa de acerto por tipo de desafio.
        
        Args:
            user_id: ID do utilizador
            challenge_type: Tipo específico ou None para todos
        
        Returns:
            Dicionário com taxas de acerto
        """
        self.initialize_user(user_id)
        user = self.user_data[user_id]
        
        if challenge_type:
            return {
                'type': challenge_type,
                **user['by_type'][challenge_type]
            }
        
        return {
            'global_accuracy': user['accuracy_rate'],
            'by_type': user['by_type']
        }
    
    def get_progress_report(self, user_id: str) -> Dict:
        """
        Gera relatório de progresso cognitivo.
        
        Args:
            user_id: ID do utilizador
        
        Returns:
            Relatório completo de progresso
        """
        self.initialize_user(user_id)
        user = self.user_data[user_id]
        
        return {
            'user_id': user_id,
            'summary': {
                'total_challenges': user['total_challenges'],
                'correct_answers': user['correct_answers'],
                'accuracy_rate': round(user['accuracy_rate'], 2),
                'current_level': user['current_level']
            },
            'by_challenge_type': user['by_type'],
            'discovery': {
                'animals_discovered': len(user['animals_discovered']),
                'animals_list': user['animals_discovered']
            },
            'timeline': {
                'first_attempt': user['first_attempt'],
                'last_attempt': user['last_attempt']
            }
        }
    
    def get_recommended_challenges(self, user_id: str) -> List[str]:
        """
        Recomenda tipos de desafios baseado no desempenho.
        
        Args:
            user_id: ID do utilizador
        
        Returns:
            Lista de tipos recomendados (ordenados por prioridade)
        """
        self.initialize_user(user_id)
        user = self.user_data[user_id]
        
        # Ordenar tipos por accuracy (menor para maior)
        types_by_accuracy = sorted(
            user['by_type'].items(),
            key=lambda x: x[1]['accuracy']
        )
        
        # Recomendar tipos com menor accuracy primeiro
        return [t[0] for t in types_by_accuracy if t[1]['total'] < 10]
    
    def _calculate_level(self, user: Dict) -> int:
        """Calcula nível baseado em desempenho"""
        total = user['total_challenges']
        accuracy = user['accuracy_rate']
        
        if total < 5:
            return 1
        elif total < 15 and accuracy >= 60:
            return 2
        elif total < 30 and accuracy >= 70:
            return 3
        elif total < 50 and accuracy >= 80:
            return 4
        elif accuracy >= 85:
            return 5
        
        return max(1, user['current_level'])
    
    def _calculate_points(self, is_correct: bool, time_taken: float) -> int:
        """Calcula pontos baseado em correção e tempo"""
        if not is_correct:
            return 0
        
        base_points = 10
        
        # Bonus por rapidez (< 10 segundos = +5 pontos)
        if time_taken < 10:
            base_points += 5
        elif time_taken < 20:
            base_points += 2
        
        return base_points
    
    def export_analytics(self, user_id: str) -> Dict:
        """
        Exporta todos os analytics em formato compatível com Inven!RA.
        
        Args:
            user_id: ID do utilizador
        
        Returns:
            Dados formatados para Inven!RA
        """
        self.initialize_user(user_id)
        user = self.user_data[user_id]
        
        return {
            'studentId': user_id,
            'activityId': 'dia-noite-animals',
            'metrics': {
                'totalResponses': user['total_challenges'],
                'correctResponses': user['correct_answers'],
                'accuracyRate': user['accuracy_rate'],
                'currentLevel': user['current_level'],
                'animalsDiscovered': len(user['animals_discovered'])
            },
            'byType': user['by_type'],
            'timestamp': datetime.now().isoformat()
        }


# Instância global (singleton para simplificar)
cognitive_analytics = CognitiveAnalytics()
