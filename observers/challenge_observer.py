"""
Challenge Observer - Interface Abstrata do Padrão Observer

Define a interface que todos os observers concretos devem implementar.
Observers são notificados quando eventos relacionados a desafios ocorrem.

Padrão: Observer (Comportamental)
Papel: Observer (interface abstrata)
"""

from abc import ABC, abstractmethod


class ChallengeObserver(ABC):
    """
    Interface abstrata para observers de eventos de desafio.

    Observers implementam esta interface para receber notificações
    quando os desafios são completados, permitindo que múltiplos sistemas
    reajam ao mesmo evento sem acoplamento direto.
    """

    @abstractmethod
    def on_challenge_completed(self, user_id: str, challenge, answer: str,
                               time_taken: float, is_correct: bool) -> None:
        """
        Método chamado quando um desafio é completado.

        Args:
            user_id: Identificador do usuário que completou o desafio
            challenge: Instância do desafio completado (Challenge object)
            answer: Resposta fornecida pelo usuário
            time_taken: Tempo em segundos que o usuário levou
            is_correct: Se a resposta está correta ou não
        """
        pass

    @abstractmethod
    def on_challenge_started(self, user_id: str, challenge) -> None:
        """
        Método chamado quando um desafio é iniciado.

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio iniciado
        """
        pass

    def on_challenge_skipped(self, user_id: str, challenge) -> None:
        """
        Método opcional chamado quando um desafio é pulado.
        Implementação padrão vazia (hook method).

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio pulado
        """
        pass
