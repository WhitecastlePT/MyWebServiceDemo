"""
Configurações Centralizadas do Jogo - Dia & Noite: O Mundo dos Animais

ANTI-PADRÃO CORRIGIDO: Magic Numbers
Anteriormente, valores numéricos estavam espalhados pelo código (hardcoded).
Agora todas as configurações estão centralizadas neste ficheiro, permitindo:
- Fácil ajuste de valores sem modificar lógica
- Documentação clara do significado de cada valor
- Configuração diferente por ambiente (dev/prod)
- Balanceamento do jogo sem tocar no código

Autores: Henrique Crachat (2501450)
"""
from typing import Dict


class LevelSettings:
    """
    Configurações de níveis baseados em desempenho cognitivo.

    Níveis são calculados com base no total de desafios completados
    e na taxa de acerto (accuracy). Quanto melhor o desempenho,
    mais rápido o jogador progride.
    """

    # Thresholds para cálculo de nível
    # Formato: (min_challenges, min_accuracy) -> level
    LEVEL_THRESHOLDS = [
        {'level': 1, 'min_challenges': 0, 'min_accuracy': 0},
        {'level': 2, 'min_challenges': 5, 'min_accuracy': 60},
        {'level': 3, 'min_challenges': 15, 'min_accuracy': 70},
        {'level': 4, 'min_challenges': 30, 'min_accuracy': 80},
        {'level': 5, 'min_challenges': 50, 'min_accuracy': 85},
    ]

    @staticmethod
    def calculate_level(total_challenges: int, accuracy_rate: float, current_level: int) -> int:
        """
        Calcula o nível baseado em desempenho.

        Args:
            total_challenges: Total de desafios completados
            accuracy_rate: Taxa de acerto (0-100)
            current_level: Nível atual do jogador

        Returns:
            Nível calculado
        """
        for threshold in reversed(LevelSettings.LEVEL_THRESHOLDS):
            if (total_challenges >= threshold['min_challenges'] and
                    accuracy_rate >= threshold['min_accuracy']):
                return threshold['level']

        # Nunca regredir de nível
        return max(1, current_level)


class PointsSettings:
    """
    Configurações de pontos por desafio completado.

    Pontos recompensam respostas corretas e rapidez. São usados
    para rankings e podem ser diferentes de XP (experiência).
    """

    # Pontos base por resposta correta
    BASE_POINTS = 10

    # Bónus por velocidade de resposta
    # Formato: (max_time_seconds, bonus_points)
    SPEED_BONUSES = [
        {'max_time': 10, 'bonus': 5},  # Muito rápido
        {'max_time': 20, 'bonus': 2},  # Rápido
    ]

    @staticmethod
    def calculate_points(is_correct: bool, time_taken: float) -> int:
        """
        Calcula pontos baseado em correção e tempo.

        Args:
            is_correct: Se a resposta está correta
            time_taken: Tempo decorrido em segundos

        Returns:
            Pontos ganhos
        """
        if not is_correct:
            return 0

        points = PointsSettings.BASE_POINTS

        # Aplicar bónus de velocidade
        for bonus in PointsSettings.SPEED_BONUSES:
            if time_taken < bonus['max_time']:
                points += bonus['bonus']
                break  # Aplicar apenas o maior bónus

        return points


class XPSettings:
    """
    Configurações de experiência (XP) e progressão de níveis.

    XP é diferente de pontos - determina progressão através dos níveis.
    Diferentes tipos de desafios concedem diferentes quantidades de XP.
    """

    # XP base por desafio completado corretamente
    BASE_XP = 10

    # Multiplicadores de XP por tipo de desafio
    # Desafios mais difíceis concedem mais XP
    XP_MULTIPLIERS = {
        'audio': 1.0,           # Padrão
        'visual': 1.1,          # +10% XP
        'habitat': 1.2,         # +20% XP
        'classification': 1.5   # +50% XP (mais difícil)
    }

    # Bónus de XP por velocidade
    # Formato: (max_time_seconds, bonus_xp)
    SPEED_XP_BONUSES = [
        {'max_time': 5, 'bonus': 10},   # Extremamente rápido
        {'max_time': 10, 'bonus': 5},   # Muito rápido
        {'max_time': 20, 'bonus': 2},   # Rápido
    ]

    # Bónus de XP por dificuldade
    DIFFICULTY_XP_BONUSES = {
        'easy': 0,
        'medium': 5,
        'hard': 10
    }

    # Configuração de níveis e XP necessário
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

    @staticmethod
    def calculate_xp(challenge_type: str, time_taken: float,
                     difficulty: str = 'medium') -> int:
        """
        Calcula XP ganho por desafio completado.

        Args:
            challenge_type: Tipo do desafio (audio, visual, etc.)
            time_taken: Tempo decorrido em segundos
            difficulty: Dificuldade do desafio

        Returns:
            XP ganho
        """
        # XP base
        xp = XPSettings.BASE_XP

        # Aplicar multiplicador por tipo
        type_multiplier = XPSettings.XP_MULTIPLIERS.get(challenge_type, 1.0)

        # Aplicar bónus de dificuldade
        difficulty_bonus = XPSettings.DIFFICULTY_XP_BONUSES.get(difficulty, 0)

        # Calcular XP com multiplicador
        xp = int((xp + difficulty_bonus) * type_multiplier)

        # Aplicar bónus de velocidade
        for bonus in XPSettings.SPEED_XP_BONUSES:
            if time_taken < bonus['max_time']:
                xp += bonus['bonus']
                break  # Aplicar apenas o maior bónus

        return xp


class RecommendationSettings:
    """
    Configurações para sistema de recomendação de desafios.

    O sistema recomenda tipos de desafios onde o jogador tem
    menor desempenho, incentivando prática balanceada.
    """

    # Mínimo de tentativas antes de recomendar
    MIN_ATTEMPTS_FOR_RECOMMENDATION = 10

    @staticmethod
    def should_recommend(total_attempts: int) -> bool:
        """
        Verifica se um tipo de desafio deve ser recomendado.

        Args:
            total_attempts: Total de tentativas neste tipo

        Returns:
            True se deve recomendar prática adicional
        """
        return total_attempts < RecommendationSettings.MIN_ATTEMPTS_FOR_RECOMMENDATION


class GameConfig:
    """
    Configuração geral do jogo.

    Classe utilitária que agrega todas as configurações e fornece
    métodos helper para acesso fácil.
    """

    levels = LevelSettings
    points = PointsSettings
    xp = XPSettings
    recommendations = RecommendationSettings

    @classmethod
    def get_all_settings(cls) -> Dict:
        """
        Retorna todas as configurações em formato dict.

        Útil para export/debugging.

        Returns:
            Dicionário com todas as configurações
        """
        return {
            'levels': {
                'thresholds': cls.levels.LEVEL_THRESHOLDS,
            },
            'points': {
                'base': cls.points.BASE_POINTS,
                'speed_bonuses': cls.points.SPEED_BONUSES,
            },
            'xp': {
                'base': cls.xp.BASE_XP,
                'multipliers': cls.xp.XP_MULTIPLIERS,
                'speed_bonuses': cls.xp.SPEED_XP_BONUSES,
                'difficulty_bonuses': cls.xp.DIFFICULTY_XP_BONUSES,
                'levels': cls.xp.LEVELS,
            },
            'recommendations': {
                'min_attempts': cls.recommendations.MIN_ATTEMPTS_FOR_RECOMMENDATION,
            }
        }

    @classmethod
    def export_to_json(cls) -> str:
        """
        Exporta configurações para JSON.

        Returns:
            String JSON com configurações
        """
        import json
        return json.dumps(cls.get_all_settings(), indent=2, ensure_ascii=False)
