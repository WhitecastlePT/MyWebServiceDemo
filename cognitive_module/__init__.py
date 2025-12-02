"""
Módulo Cognitivo - Henrique Crachat (2501450)

Integração do padrão Factory Method com analytics de desempenho cognitivo.

Autor: Henrique Crachat (2501450@estudante.uab.pt)
"""

from cognitive_module.cognitive_analytics import cognitive_analytics, CognitiveAnalytics
from cognitive_module.cognitive_endpoints import register_cognitive_routes

__all__ = [
    'cognitive_analytics',
    'CognitiveAnalytics',
    'register_cognitive_routes'
]

__version__ = '1.0.0'
__author__ = 'Henrique Crachat (2501450)'
