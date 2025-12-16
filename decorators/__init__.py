"""
Decorators para adicionar funcionalidades extras aos Challenges.

Padrão de Estrutura: Decorator
Permite adicionar responsabilidades a objetos dinamicamente.

Autores: Henrique Crachat (2501450) & Fábio Amado (2501444)
UC: Arquitetura e Padrões de Software
Universidade Aberta
"""

from decorators.challenge_decorator import ChallengeDecorator
from decorators.timed_decorator import TimedChallengeDecorator

__all__ = [
    'ChallengeDecorator',
    'TimedChallengeDecorator'
]
