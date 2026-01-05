"""
Level Progression Observer - Observer Concreto para Progressão de Níveis

Implementa o padrão Observer para gerenciar sistema de níveis
e progressão dos utilizadores baseado em desempenho.

Padrão: Observer (Comportamental)
Papel: ConcreteObserver
"""

from observers.challenge_observer import ChallengeObserver
from typing import Dict, List, Optional
from datetime import datetime


class LevelProgressionObserver(ChallengeObserver):
    """
    Observer responsável por gerenciar progressão de níveis.

    Monitora desempenho dos utilizadores e gerencia:
    - Progressão de níveis
    - Experiência (XP)
    - Requisitos para próximo nível
    - Notificações de level up
    """

    # Configuração de níveis
    LEVELS = {
        1: {'name': 'Explorador Iniciante', 'xp_required': 0, 'icon': '🌱'},
        2: {'name': 'Observador Curioso', 'xp_required': 100, 'icon': '🔍'},
        3: {'name': 'Conhecedor da Fauna', 'xp_required': 300, 'icon': '🦊'},
        4: {'name': 'Especialista Animal', 'xp_required': 600, 'icon': '🦁'},
        5: {'name': 'Mestre Naturalista', 'xp_required': 1000, 'icon': '🦅'},
        6: {'name': 'Sábio da Natureza', 'xp_required': 1500, 'icon': '🌟'},
        7: {'name': 'Guardião dos Animais', 'xp_required': 2200, 'icon': '👑'},
        8: {'name': 'Lenda da Fauna', 'xp_required': 3000, 'icon': '🏆'}
    }

    # Multiplicadores de XP por tipo de desafio
    XP_MULTIPLIERS = {
        'audio': 1.0,
        'visual': 1.1,
        'habitat': 1.2,
        'classification': 1.5
    }

    def __init__(self, invenira_observer=None):
        """
        Inicializa o sistema de progressão.

        Args:
            invenira_observer: Observer opcional para notificar Inven!RA sobre level ups
        """
        # Estrutura: {user_id: {level, xp, history}}
        self.user_progression: Dict[str, Dict] = {}
        self.invenira_observer = invenira_observer

    def _initialize_user(self, user_id: str) -> None:
        """Inicializa dados de progressão para um utilizador."""
        if user_id not in self.user_progression:
            self.user_progression[user_id] = {
                'level': 1,
                'current_xp': 0,
                'total_xp_earned': 0,
                'challenges_completed': 0,
                'level_up_history': [],
                'created_at': datetime.now().isoformat()
            }

    def on_challenge_completed(self, user_id: str, challenge, answer: str,
                               time_taken: float, is_correct: bool) -> None:
        """
        Atualiza XP e nível quando desafio é completado.

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio completado
            answer: Resposta fornecida
            time_taken: Tempo decorrido em segundos
            is_correct: Se a resposta está correta
        """
        self._initialize_user(user_id)

        # Calcular XP ganho
        xp_earned = self._calculate_xp(challenge, is_correct, time_taken)

        # Atualizar progresso do utilizador
        user = self.user_progression[user_id]
        old_level = user['level']

        user['current_xp'] += xp_earned
        user['total_xp_earned'] += xp_earned
        user['challenges_completed'] += 1

        # Verificar level up
        new_level = self._check_level_up(user_id)

        if new_level > old_level:
            self._handle_level_up(user_id, old_level, new_level)

        # Log de XP ganho
        xp_message = f"+{xp_earned} XP" if is_correct else "+0 XP"
        print(f"[LevelProgressionObserver] {user_id} - {xp_message} - "
              f"Level {user['level']} ({user['current_xp']} XP)")

    def on_challenge_started(self, user_id: str, challenge) -> None:
        """
        Inicializa utilizador quando inicia um desafio.

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio iniciado
        """
        self._initialize_user(user_id)

    def _calculate_xp(self, challenge, is_correct: bool, time_taken: float) -> int:
        """
        Calcula XP ganho baseado em múltiplos fatores.

        Args:
            challenge: Instância do desafio
            is_correct: Se resposta está correta
            time_taken: Tempo decorrido

        Returns:
            Quantidade de XP ganho
        """
        if not is_correct:
            return 0

        # XP base
        base_xp = 10

        # Multiplicador por tipo de desafio
        challenge_type = challenge.get_challenge_type()
        type_multiplier = self.XP_MULTIPLIERS.get(challenge_type, 1.0)

        # Bônus por velocidade
        speed_bonus = 0
        if time_taken < 5:
            speed_bonus = 10
        elif time_taken < 10:
            speed_bonus = 5
        elif time_taken < 20:
            speed_bonus = 2

        # Bônus por dificuldade (se existir)
        difficulty_bonus = 0
        if hasattr(challenge, 'difficulty'):
            difficulty_map = {'easy': 0, 'medium': 5, 'hard': 10}
            difficulty_bonus = difficulty_map.get(challenge.difficulty, 0)

        # Cálculo final
        total_xp = int((base_xp + difficulty_bonus) * type_multiplier + speed_bonus)

        return total_xp

    def _check_level_up(self, user_id: str) -> int:
        """
        Verifica se utilizador subiu de nível.

        Args:
            user_id: Identificador do usuário

        Returns:
            Nível atual do utilizador
        """
        user = self.user_progression[user_id]
        current_xp = user['current_xp']
        current_level = user['level']

        # Verificar se atingiu XP para próximo nível
        for level, config in sorted(self.LEVELS.items()):
            if current_xp >= config['xp_required']:
                current_level = level
            else:
                break

        user['level'] = current_level
        return current_level

    def _handle_level_up(self, user_id: str, old_level: int, new_level: int) -> None:
        """
        Processa level up do utilizador.

        Args:
            user_id: Identificador do usuário
            old_level: Nível anterior
            new_level: Novo nível
        """
        user = self.user_progression[user_id]

        # Registrar no histórico
        level_up_event = {
            'timestamp': datetime.now().isoformat(),
            'old_level': old_level,
            'new_level': new_level,
            'total_xp': user['total_xp_earned'],
            'challenges_completed': user['challenges_completed']
        }
        user['level_up_history'].append(level_up_event)

        # Notificar utilizador
        level_config = self.LEVELS[new_level]
        print(f"\n{'='*50}")
        print(f"*** LEVEL UP! ***")
        print(f"Utilizador: {user_id}")
        print(f"Nivel {old_level} -> Nivel {new_level}")
        print(f"{level_config['name']}")
        print(f"{'='*50}\n")

        # Notificar Inven!RA se observer disponível
        if self.invenira_observer:
            metrics = {
                'total_challenges': user['challenges_completed'],
                'total_xp': user['total_xp_earned'],
                'accuracy_rate': 0  # Seria calculado se tivéssemos acesso ao analytics
            }
            self.invenira_observer.notify_level_up(user_id, new_level, metrics)

    def get_user_progress(self, user_id: str) -> Dict:
        """
        Retorna progresso completo do utilizador.

        Args:
            user_id: Identificador do usuário

        Returns:
            Dados de progressão
        """
        self._initialize_user(user_id)
        user = self.user_progression[user_id]

        current_level = user['level']
        current_xp = user['current_xp']

        # Calcular XP para próximo nível
        next_level = current_level + 1 if current_level < max(self.LEVELS.keys()) else None
        xp_for_next = None
        xp_progress_percentage = 100

        if next_level and next_level in self.LEVELS:
            xp_required = self.LEVELS[next_level]['xp_required']
            xp_current_level = self.LEVELS[current_level]['xp_required']
            xp_for_next = xp_required - current_xp
            xp_needed_for_level = xp_required - xp_current_level
            xp_progress = current_xp - xp_current_level
            xp_progress_percentage = (xp_progress / xp_needed_for_level * 100) if xp_needed_for_level > 0 else 100

        return {
            'current_level': {
                'number': current_level,
                'name': self.LEVELS[current_level]['name'],
                'icon': self.LEVELS[current_level]['icon']
            },
            'xp': {
                'current': current_xp,
                'total_earned': user['total_xp_earned'],
                'for_next_level': xp_for_next,
                'progress_percentage': round(xp_progress_percentage, 1)
            },
            'next_level': {
                'number': next_level,
                'name': self.LEVELS[next_level]['name'] if next_level and next_level in self.LEVELS else None,
                'icon': self.LEVELS[next_level]['icon'] if next_level and next_level in self.LEVELS else None
            } if next_level else None,
            'statistics': {
                'challenges_completed': user['challenges_completed'],
                'level_ups': len(user['level_up_history']),
                'member_since': user['created_at']
            },
            'level_up_history': user['level_up_history'][-5:]  # Últimos 5 level ups
        }

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Retorna ranking de utilizadores por XP.

        Args:
            limit: Número máximo de resultados

        Returns:
            Lista ordenada de utilizadores
        """
        leaderboard = []

        for user_id, data in self.user_progression.items():
            leaderboard.append({
                'user_id': user_id,
                'level': data['level'],
                'level_name': self.LEVELS[data['level']]['name'],
                'total_xp': data['total_xp_earned'],
                'challenges_completed': data['challenges_completed']
            })

        # Ordenar por XP total (decrescente)
        leaderboard.sort(key=lambda x: x['total_xp'], reverse=True)

        return leaderboard[:limit]

    def award_bonus_xp(self, user_id: str, amount: int, reason: str) -> None:
        """
        Concede XP bônus ao utilizador.

        Args:
            user_id: Identificador do usuário
            amount: Quantidade de XP bônus
            reason: Motivo do bônus
        """
        self._initialize_user(user_id)
        user = self.user_progression[user_id]

        old_level = user['level']
        user['current_xp'] += amount
        user['total_xp_earned'] += amount

        new_level = self._check_level_up(user_id)

        if new_level > old_level:
            self._handle_level_up(user_id, old_level, new_level)

        print(f"[LevelProgressionObserver] Bônus XP concedido - "
              f"{user_id}: +{amount} XP ({reason})")
