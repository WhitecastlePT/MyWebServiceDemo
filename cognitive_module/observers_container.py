"""
Contentor para instâncias de Observers - Henrique Crachat (2501450)

Este módulo implementa o padrão Dependency Injection para resolver
o anti-padrão de Singleton Abuse / Global State.

Anteriormente, os observers eram variáveis globais, o que dificultava:
- Testes unitários (estado partilhado)
- Multi-tenancy (múltiplas instâncias)
- Threading (concorrência)

Com ObserversContainer, as instâncias são geridas num contentor que pode
ser injetado via parâmetros, permitindo flexibilidade e testabilidade.

Autor: Henrique Crachat (2501450@estudante.uab.pt)
"""
from cognitive_module.cognitive_analytics import CognitiveAnalytics


class ObserversContainer:
    """
    Contentor para instâncias de observers e analytics.

    Este padrão resolve o anti-padrão de Singleton Abuse ao encapsular
    todas as dependências num único objeto que pode ser injetado.

    Benefícios:
    - Testes: Pode criar containers diferentes para cada teste
    - Isolamento: Cada instância da aplicação tem seu próprio estado
    - Threading: Permite instâncias thread-safe
    - Flexibilidade: Fácil substituir implementações para testes

    Example:
        >>> container = ObserversContainer()
        >>> challenge.attach(container.analytics_observer)
        >>> challenge.notify_started(user_id)
    """

    def __init__(self, cognitive_analytics=None):
        """
        Inicializa o contentor com todas as dependências.

        Args:
            cognitive_analytics: Instância de CognitiveAnalytics (opcional)
                                Se None, cria uma nova instância
        """
        # Import aqui para evitar circular dependency
        from observers.analytics_observer import AnalyticsObserver
        from observers.achievement_observer import AchievementObserver
        from observers.invenira_observer import InveniraObserver
        from observers.level_progression_observer import LevelProgressionObserver

        # Cognitive Analytics
        self.cognitive_analytics = cognitive_analytics or CognitiveAnalytics()

        # Observers
        self.analytics_observer = AnalyticsObserver(self.cognitive_analytics)
        self.achievement_observer = AchievementObserver()
        self.invenira_observer = InveniraObserver()
        self.level_progression_observer = LevelProgressionObserver(
            invenira_observer=self.invenira_observer
        )

    def attach_all_to_challenge(self, challenge):
        """
        Anexa todos os observers a um desafio.

        Helper method que centraliza o registro de observers,
        facilitando manutenção e garantindo consistência.

        Args:
            challenge: Instância de Challenge

        Returns:
            Challenge com observers anexados (para encadeamento)
        """
        challenge.attach(self.analytics_observer)
        challenge.attach(self.achievement_observer)
        challenge.attach(self.invenira_observer)
        challenge.attach(self.level_progression_observer)
        return challenge
