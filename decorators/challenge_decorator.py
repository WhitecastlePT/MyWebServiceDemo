"""
Decorator base abstrato para Challenges.

Padrão de Estrutura: Decorator
Este é o componente abstrato do padrão Decorator.

Autores: Henrique Crachat (2501450) & Fábio Amado (2501444)
UC: Arquitetura e Padrões de Software
Universidade Aberta
"""
from abc import ABC
from models.challenge import Challenge
from typing import List, Dict, Any


class ChallengeDecorator(Challenge, ABC):
    """
    Decorator abstrato para adicionar funcionalidades a Challenges.

    PADRÃO DE ESTRUTURA: Decorator

    >>> factory = ChallengeFactory()
    >>> base_challenge = factory.create_challenge('audio', animal_id=1)
    >>> timed_challenge = TimedChallengeDecorator(base_challenge, time_limit=30)

    """

    def __init__(self, challenge: Challenge):
        """
        Inicializa o decorator com um Challenge.

        Args:
            challenge: Challenge a ser decorado (pode ser concreto ou já decorado)
        """
        # Não chamar super().__init__() pois o challenge já está inicializado
        self._challenge = challenge

        # Delegar atributos básicos ao challenge decorado
        self.animal_id = challenge.animal_id
        self.difficulty = challenge.difficulty
        self.challenge_id = challenge.challenge_id
        self.correct_answer = challenge.correct_answer

    def get_question(self) -> str:
        """
        Delega ao challenge decorado.
        Subclasses podem sobrescrever para modificar a pergunta.

        Returns:
            Pergunta do desafio decorado
        """
        return self._challenge.get_question()

    def get_options(self) -> List[str]:
        """
        Delega ao challenge decorado.
        Subclasses podem sobrescrever para modificar as opções.

        Returns:
            Opções do desafio decorado
        """
        return self._challenge.get_options()

    def get_challenge_type(self) -> str:
        """
        Delega ao challenge decorado.
        Mantém o tipo original do challenge.

        Returns:
            Tipo do desafio decorado
        """
        return self._challenge.get_challenge_type()

    def validate_answer(self, answer: str) -> bool:
        """
        Delega ao challenge decorado.
        Subclasses podem sobrescrever para adicionar validações extras.

        Args:
            answer: Resposta do aluno

        Returns:
            True se correto, False caso contrário
        """
        return self._challenge.validate_answer(answer)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário.
        Subclasses devem sobrescrever para incluir dados extras.

        Returns:
            Dicionário com dados do desafio decorado
        """
        base_dict = self._challenge.to_dict()
        base_dict['decorated'] = True
        base_dict['decorator_type'] = self.__class__.__name__
        return base_dict

    def get_wrapped_challenge(self) -> Challenge:
        """
        Retorna o challenge sendo decorado.
        Útil para inspeção e unwrapping.

        Returns:
            Challenge original (pode ser concreto ou outro decorator)
        """
        return self._challenge

    def get_base_challenge(self) -> Challenge:
        """
        Retorna o challenge base (não decorado).
        Percorre toda a cadeia de decorators.

        Returns:
            Challenge concreto na base da cadeia
        """
        current = self._challenge
        while isinstance(current, ChallengeDecorator):
            current = current.get_wrapped_challenge()
        return current

    def __repr__(self) -> str:
        """Representação em string mostrando cadeia de decorators"""
        return f"{self.__class__.__name__}({self._challenge})"
