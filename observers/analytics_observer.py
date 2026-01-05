"""
Analytics Observer - Observer Concreto para Analytics Cognitivo

Implementa o padrão Observer para registar estatísticas de desafios
no sistema de analytics cognitivo existente.

Padrão: Observer (Comportamental)
Papel: ConcreteObserver
"""

from observers.challenge_observer import ChallengeObserver
from cognitive_module.cognitive_analytics import CognitiveAnalytics
from typing import Optional


class AnalyticsObserver(ChallengeObserver):
    """
    Observer responsável por registar estatísticas no sistema de analytics.

    Quando notificado de um evento de desafio, atualiza as métricas
    cognitivas do utilizador no sistema CognitiveAnalytics.
    """

    def __init__(self, analytics: Optional[CognitiveAnalytics] = None):
        """
        Inicializa o observer de analytics.

        Args:
            analytics: Instância de CognitiveAnalytics. Se None, usa a instância global.
        """
        from cognitive_module.cognitive_analytics import cognitive_analytics
        self.analytics = analytics or cognitive_analytics

    def on_challenge_completed(self, user_id: str, challenge, answer: str,
                               time_taken: float, is_correct: bool) -> None:
        """
        Registar resposta no sistema de analytics quando desafio é completado.

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio completado
            answer: Resposta fornecida
            time_taken: Tempo decorrido em segundos
            is_correct: Se a resposta está correta
        """
        # Registar resposta no sistema de analytics
        result = self.analytics.record_response(
            user_id=user_id,
            challenge=challenge,
            answer=answer,
            time_taken=time_taken
        )

        # Log opcional para debugging (pode ser removido em produção)
        status = "CORRECT" if is_correct else "INCORRECT"
        print(f"[AnalyticsObserver] User {user_id} - {status} - "
              f"Accuracy: {result['current_accuracy']:.1f}% - "
              f"Level: {result['current_level']}")

    def on_challenge_started(self, user_id: str, challenge) -> None:
        """
        Inicializar utilizador no sistema de analytics se necessário.

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio iniciado
        """
        # Garantir que o utilizador está inicializado no sistema
        self.analytics.initialize_user(user_id)

        challenge_type = challenge.get_challenge_type()
        print(f"[AnalyticsObserver] User {user_id} started {challenge_type} challenge")

    def on_challenge_skipped(self, user_id: str, challenge) -> None:
        """
        Registar quando um desafio é pulado (opcional).

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio pulado
        """
        challenge_type = challenge.get_challenge_type()
        print(f"[AnalyticsObserver] User {user_id} skipped {challenge_type} challenge")

    def get_user_progress(self, user_id: str) -> dict:
        """
        Obter relatório de progresso do utilizador.

        Args:
            user_id: Identificador do usuário

        Returns:
            Dicionário com progresso completo
        """
        return self.analytics.get_progress_report(user_id)

    def export_for_invenira(self, user_id: str) -> dict:
        """
        Exportar dados em formato compatível com Inven!RA.

        Args:
            user_id: Identificador do usuário

        Returns:
            Dados formatados para plataforma Inven!RA
        """
        return self.analytics.export_analytics(user_id)
