"""
Level Progression Observer - Observer Concreto para Progressão de Níveis

Implementa o padrão Observer para gerenciar sistema de níveis
e progressão dos utilizadores baseado em desempenho.

ANTI-PADRÃO CORRIGIDO: Magic Numbers
Valores de XP, níveis e multiplicadores agora vêm de config.game_settings.

Padrão: Observer (Comportamental)
Papel: ConcreteObserver
"""

from observers.challenge_observer import ChallengeObserver
from typing import Dict, List, Optional
from datetime import datetime
from config.game_settings import XPSettings


class LevelProgressionObserver(ChallengeObserver):
    """
    Observer responsável por gerenciar progressão de níveis.

    Monitora desempenho dos utilizadores e gerencia:
    - Progressão de níveis
    - Experiência (XP)
    - Requisitos para próximo nível
    - Notificações de level up

    Configurações de XP e níveis vêm de config.game_settings.XPSettings.
    """

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

        # Usar configurações centralizadas para cálculo de XP
        challenge_type = challenge.get_challenge_type()
        difficulty = getattr(challenge, 'difficulty', 'medium')

        return XPSettings.calculate_xp(
            challenge_type=challenge_type,
            time_taken=time_taken,
            difficulty=difficulty
        )

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
        for level, config in sorted(XPSettings.LEVELS.items()):
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
        level_config = XPSettings.LEVELS[new_level]
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
        next_level = current_level + 1 if current_level < max(XPSettings.LEVELS.keys()) else None
        xp_for_next = None
        xp_progress_percentage = 100

        if next_level and next_level in XPSettings.LEVELS:
            xp_required = XPSettings.LEVELS[next_level]['xp_required']
            xp_current_level = XPSettings.LEVELS[current_level]['xp_required']
            xp_for_next = xp_required - current_xp
            xp_needed_for_level = xp_required - xp_current_level
            xp_progress = current_xp - xp_current_level
            xp_progress_percentage = (xp_progress / xp_needed_for_level * 100) if xp_needed_for_level > 0 else 100

        return {
            'current_level': {
                'number': current_level,
                'name': XPSettings.LEVELS[current_level]['name'],
                'icon': XPSettings.LEVELS[current_level]['icon']
            },
            'xp': {
                'current': current_xp,
                'total_earned': user['total_xp_earned'],
                'for_next_level': xp_for_next,
                'progress_percentage': round(xp_progress_percentage, 1)
            },
            'next_level': {
                'number': next_level,
                'name': XPSettings.LEVELS[next_level]['name'] if next_level and next_level in XPSettings.LEVELS else None,
                'icon': XPSettings.LEVELS[next_level]['icon'] if next_level and next_level in XPSettings.LEVELS else None
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
                'level_name': XPSettings.LEVELS[data['level']]['name'],
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
