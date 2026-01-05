"""
Observers Module - Implementação do Padrão Observer

Este módulo contém a implementação do padrão comportamental Observer
para notificar múltiplos sistemas quando um desafio é completado.

Observer Pattern permite que objetos sejam notificados de mudanças
em outros objetos sem acoplamento forte entre eles.
"""

from observers.challenge_observer import ChallengeObserver
from observers.analytics_observer import AnalyticsObserver
from observers.achievement_observer import AchievementObserver
from observers.invenira_observer import InveniraObserver
from observers.level_progression_observer import LevelProgressionObserver

__all__ = [
    'ChallengeObserver',
    'AnalyticsObserver',
    'AchievementObserver',
    'InveniraObserver',
    'LevelProgressionObserver'
]
