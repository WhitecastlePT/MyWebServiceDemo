"""
Achievement Observer - Observer Concreto para Sistema de Conquistas

Implementa o padrão Observer para gerenciar conquistas (achievements)
dos utilizadores baseado em seu desempenho nos desafios.

Padrão: Observer (Comportamental)
Papel: ConcreteObserver
"""

from observers.challenge_observer import ChallengeObserver
from typing import Dict, List, Set
from datetime import datetime


class AchievementObserver(ChallengeObserver):
    """
    Observer responsável por gerenciar e desbloquear conquistas.

    Monitora o desempenho dos utilizadores e desbloqueia badges/conquistas
    quando critérios específicos são atingidos.
    """

    # Definição de conquistas disponíveis
    ACHIEVEMENTS = {
        'first_steps': {
            'name': 'Primeiros Passos',
            'description': 'Complete seu primeiro desafio',
            'icon': '🎯',
            'criteria': lambda stats: stats['total_completed'] >= 1
        },
        'speed_master': {
            'name': 'Mestre da Velocidade',
            'description': 'Responda corretamente em menos de 5 segundos',
            'icon': '⚡',
            'criteria': lambda stats: stats['fastest_time'] < 5.0 and stats['fastest_time'] > 0
        },
        'perfect_streak': {
            'name': 'Sequência Perfeita',
            'description': 'Acerte 5 desafios seguidos',
            'icon': '🔥',
            'criteria': lambda stats: stats['current_streak'] >= 5
        },
        'audio_expert': {
            'name': 'Especialista em Áudio',
            'description': 'Complete 10 desafios de áudio',
            'icon': '🎵',
            'criteria': lambda stats: stats['audio_count'] >= 10
        },
        'visual_expert': {
            'name': 'Especialista Visual',
            'description': 'Complete 10 desafios visuais',
            'icon': '👁️',
            'criteria': lambda stats: stats['visual_count'] >= 10
        },
        'habitat_explorer': {
            'name': 'Explorador de Habitats',
            'description': 'Complete 10 desafios de habitat',
            'icon': '🌍',
            'criteria': lambda stats: stats['habitat_count'] >= 10
        },
        'classifier_pro': {
            'name': 'Classificador Profissional',
            'description': 'Complete 10 desafios de classificação',
            'icon': '📊',
            'criteria': lambda stats: stats['classification_count'] >= 10
        },
        'animal_collector': {
            'name': 'Colecionador de Animais',
            'description': 'Descubra 10 animais diferentes',
            'icon': '🦁',
            'criteria': lambda stats: len(stats['animals_discovered']) >= 10
        },
        'night_owl': {
            'name': 'Coruja da Noite',
            'description': 'Complete 5 desafios noturnos',
            'icon': '🦉',
            'criteria': lambda stats: stats.get('night_challenges', 0) >= 5
        },
        'day_champion': {
            'name': 'Campeão do Dia',
            'description': 'Complete 5 desafios diurnos',
            'icon': '☀️',
            'criteria': lambda stats: stats.get('day_challenges', 0) >= 5
        },
        'persistence': {
            'name': 'Persistência',
            'description': 'Complete 50 desafios no total',
            'icon': '💪',
            'criteria': lambda stats: stats['total_completed'] >= 50
        },
        'perfectionist': {
            'name': 'Perfeccionista',
            'description': 'Mantenha 100% de acertos em 10 desafios',
            'icon': '💯',
            'criteria': lambda stats: stats['total_completed'] >= 10 and stats.get('accuracy_100', False)
        }
    }

    def __init__(self):
        """Inicializa o sistema de conquistas."""
        # Estrutura: {user_id: {'unlocked': set(), 'stats': dict()}}
        self.user_achievements: Dict[str, Dict] = {}

    def _initialize_user(self, user_id: str) -> None:
        """Inicializa dados de conquistas para um utilizador."""
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = {
                'unlocked': set(),
                'stats': {
                    'total_completed': 0,
                    'total_correct': 0,
                    'current_streak': 0,
                    'fastest_time': float('inf'),
                    'audio_count': 0,
                    'visual_count': 0,
                    'habitat_count': 0,
                    'classification_count': 0,
                    'animals_discovered': set(),
                    'night_challenges': 0,
                    'day_challenges': 0,
                    'last_result': None
                },
                'unlock_history': []
            }

    def on_challenge_completed(self, user_id: str, challenge, answer: str,
                               time_taken: float, is_correct: bool) -> None:
        """
        Atualiza estatísticas e verifica novas conquistas quando desafio é completado.

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio completado
            answer: Resposta fornecida
            time_taken: Tempo decorrido em segundos
            is_correct: Se a resposta está correta
        """
        self._initialize_user(user_id)
        stats = self.user_achievements[user_id]['stats']

        # Atualizar estatísticas básicas
        stats['total_completed'] += 1
        if is_correct:
            stats['total_correct'] += 1

        # Atualizar sequência (streak)
        if is_correct:
            stats['current_streak'] = stats.get('current_streak', 0) + 1
        else:
            stats['current_streak'] = 0

        # Atualizar tempo mais rápido
        if is_correct and time_taken < stats['fastest_time']:
            stats['fastest_time'] = time_taken

        # Atualizar contadores por tipo
        challenge_type = challenge.get_challenge_type()
        type_key = f"{challenge_type}_count"
        stats[type_key] = stats.get(type_key, 0) + 1

        # Registrar animal descoberto
        if is_correct and hasattr(challenge, 'animal_id'):
            stats['animals_discovered'].add(challenge.animal_id)

        # Verificar se mantém 100% de acertos
        stats['accuracy_100'] = (stats['total_correct'] == stats['total_completed'])

        # Verificar e desbloquear novas conquistas
        newly_unlocked = self._check_achievements(user_id)

        # Notificar conquistas desbloqueadas
        if newly_unlocked:
            for achievement_id in newly_unlocked:
                achievement = self.ACHIEVEMENTS[achievement_id]
                print(f"[AchievementObserver] ACHIEVEMENT UNLOCKED! {user_id} - "
                      f"{achievement['name']}")

    def on_challenge_started(self, user_id: str, challenge) -> None:
        """
        Inicializa utilizador quando inicia um desafio.

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio iniciado
        """
        self._initialize_user(user_id)

    def _check_achievements(self, user_id: str) -> Set[str]:
        """
        Verifica e desbloqueia conquistas baseado nas estatísticas atuais.

        Args:
            user_id: Identificador do usuário

        Returns:
            Conjunto de IDs de conquistas recém-desbloqueadas
        """
        stats = self.user_achievements[user_id]['stats']
        unlocked = self.user_achievements[user_id]['unlocked']
        newly_unlocked = set()

        for achievement_id, achievement in self.ACHIEVEMENTS.items():
            # Se já está desbloqueada, pular
            if achievement_id in unlocked:
                continue

            # Verificar critério
            if achievement['criteria'](stats):
                unlocked.add(achievement_id)
                newly_unlocked.add(achievement_id)

                # Registrar no histórico
                self.user_achievements[user_id]['unlock_history'].append({
                    'achievement_id': achievement_id,
                    'timestamp': datetime.now().isoformat(),
                    'name': achievement['name']
                })

        return newly_unlocked

    def get_user_achievements(self, user_id: str) -> Dict:
        """
        Retorna todas as conquistas do utilizador.

        Args:
            user_id: Identificador do usuário

        Returns:
            Dicionário com conquistas desbloqueadas e progresso
        """
        self._initialize_user(user_id)

        unlocked = self.user_achievements[user_id]['unlocked']
        stats = self.user_achievements[user_id]['stats']

        return {
            'total_achievements': len(self.ACHIEVEMENTS),
            'unlocked_count': len(unlocked),
            'completion_percentage': (len(unlocked) / len(self.ACHIEVEMENTS) * 100),
            'unlocked': [
                {
                    'id': aid,
                    'name': self.ACHIEVEMENTS[aid]['name'],
                    'description': self.ACHIEVEMENTS[aid]['description'],
                    'icon': self.ACHIEVEMENTS[aid]['icon']
                }
                for aid in unlocked
            ],
            'locked': [
                {
                    'id': aid,
                    'name': achievement['name'],
                    'description': achievement['description'],
                    'icon': '🔒'
                }
                for aid, achievement in self.ACHIEVEMENTS.items()
                if aid not in unlocked
            ],
            'statistics': {
                'total_completed': stats['total_completed'],
                'current_streak': stats['current_streak'],
                'fastest_time': stats['fastest_time'] if stats['fastest_time'] != float('inf') else None,
                'animals_discovered': len(stats['animals_discovered'])
            }
        }

    def get_next_achievements(self, user_id: str, limit: int = 3) -> List[Dict]:
        """
        Retorna as próximas conquistas que estão quase desbloqueadas.

        Args:
            user_id: Identificador do usuário
            limit: Número máximo de sugestões

        Returns:
            Lista de conquistas próximas com progresso
        """
        self._initialize_user(user_id)
        unlocked = self.user_achievements[user_id]['unlocked']

        suggestions = []
        for aid, achievement in self.ACHIEVEMENTS.items():
            if aid not in unlocked:
                suggestions.append({
                    'id': aid,
                    'name': achievement['name'],
                    'description': achievement['description'],
                    'icon': achievement['icon']
                })

        return suggestions[:limit]
