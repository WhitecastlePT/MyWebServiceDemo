"""
Factory Method para criação de desafios.

Padrão de Criação: Factory Method
Este é o núcleo da implementação do padrão.

Autores: Henrique Crachat (2501450)
UC: Arquitetura e Padrões de Software
Universidade Aberta
"""
from models.challenge import Challenge
from models.audio_challenge import AudioChallenge
from models.visual_challenge import VisualChallenge
from models.habitat_challenge import HabitatChallenge
from models.classification_challenge import ClassificationChallenge
from typing import Optional, Type
import random


class ChallengeFactory:
    """
    Factory Method para criação de desafios do jogo.
    
    PADRÃO DE CRIAÇÃO: Factory Method
    
    Propósito:
    --------
    Define uma interface para criar objetos (desafios), mas permite que
    as subclasses decidam qual classe instanciar. Este padrão delega
    a decisão de instanciação para o momento da execução.
    
    Problema Resolvido:
    -----------------
    No jogo "Dia & Noite", diferentes tipos de desafios precisam ser
    criados dinamicamente. Sem o padrão Factory Method, o código cliente
    precisaria conhecer todas as classes concretas e ter lógica complexa
    de if/else para decidir qual instanciar.
    
    Solução:
    -------
    A ChallengeFactory encapsula a lógica de criação e fornece um
    método simples (create_challenge) que retorna o desafio apropriado
    sem que o cliente precise conhecer os detalhes de implementação.
    
    Vantagens:
    ---------
    1. Desacoplamento: Código cliente não depende de classes concretas
    2. Extensibilidade: Novos tipos adicionados facilmente via register
    3. Manutenibilidade: Lógica de criação centralizada
    4. Testabilidade: Fácil mockar para testes unitários
    5. Single Responsibility: Criação separada da lógica de negócio
    
    Participantes do Padrão:
    ----------------------
    - Product (Challenge): Interface abstrata
    - ConcreteProducts: AudioChallenge, VisualChallenge, etc.
    - Creator (ChallengeFactory): Esta classe
    - Client: App.py e endpoints da API
    
    Example:
    -------
    >>> # Cliente não precisa conhecer classes concretas
    >>> factory = ChallengeFactory()
    >>> challenge = factory.create_challenge('audio', animal_id=1)
    >>> print(challenge.get_question())
    "🔊 Que animal produz este som?"
    
    >>> # Adicionar novo tipo dinamicamente
    >>> factory.register_challenge_type('night', NightChallenge)
    """
    
    # Mapeamento de tipos para classes (registro de produtos)
    _challenge_types: dict[str, Type[Challenge]] = {
        'audio': AudioChallenge,
        'visual': VisualChallenge,
        'habitat': HabitatChallenge,
        'classification': ClassificationChallenge
    }
    
    @staticmethod
    def create_challenge(challenge_type: str, animal_id: int, 
                        difficulty: int = 1) -> Challenge:
        """
        Método Factory para criar desafios.
        
        Este é o método central do padrão Factory Method.
        Encapsula a lógica de decisão sobre qual classe concreta instanciar.
        
        Args:
            challenge_type: Tipo do desafio ('audio', 'visual', 'habitat', 'classification')
            animal_id: ID do animal para o desafio
            difficulty: Nível de dificuldade (1-5)
        
        Returns:
            Instância concreta de Challenge
        
        Raises:
            ValueError: Se o tipo de desafio for inválido
        
        Example:
            >>> challenge = ChallengeFactory.create_challenge('audio', animal_id=1)
            >>> isinstance(challenge, AudioChallenge)
            True
            
            >>> challenge = ChallengeFactory.create_challenge('invalid', animal_id=1)
            ValueError: Tipo de desafio inválido: invalid
        """
        challenge_class = ChallengeFactory._challenge_types.get(challenge_type)
        
        if challenge_class is None:
            available_types = ', '.join(ChallengeFactory._challenge_types.keys())
            raise ValueError(
                f"Tipo de desafio inválido: '{challenge_type}'. "
                f"Tipos disponíveis: {available_types}"
            )
        
        # Instanciar e retornar o desafio concreto
        return challenge_class(animal_id, difficulty)
    
    @staticmethod
    def create_random_challenge(animal_id: int, difficulty: int = 1) -> Challenge:
        """
        Cria um desafio aleatório para um animal.
        
        Útil para gerar variedade no jogo sem lógica adicional no cliente.
        
        Args:
            animal_id: ID do animal
            difficulty: Nível de dificuldade
        
        Returns:
            Desafio aleatório
        
        Example:
            >>> challenge = ChallengeFactory.create_random_challenge(animal_id=1)
            >>> challenge.get_challenge_type() in ['audio', 'visual', 'habitat', 'classification']
            True
        """
        challenge_type = random.choice(list(ChallengeFactory._challenge_types.keys()))
        return ChallengeFactory.create_challenge(challenge_type, animal_id, difficulty)
    
    @staticmethod
    def get_available_types() -> list[str]:
        """
        Retorna lista de tipos de desafios disponíveis.
        
        Útil para interfaces dinâmicas e validação.
        
        Returns:
            Lista com nomes dos tipos disponíveis
        
        Example:
            >>> types = ChallengeFactory.get_available_types()
            >>> 'audio' in types and 'visual' in types
            True
        """
        return list(ChallengeFactory._challenge_types.keys())
    
    @staticmethod
    def register_challenge_type(type_name: str, challenge_class: Type[Challenge]) -> None:
        """
        Permite registar novos tipos de desafios dinamicamente.
        
        Demonstra a extensibilidade do padrão Factory Method.
        Novos tipos podem ser adicionados em runtime sem modificar a factory.
        
        Args:
            type_name: Nome do novo tipo (ex: 'night', 'sound', 'quiz')
            challenge_class: Classe do desafio (deve herdar de Challenge)
        
        Raises:
            TypeError: Se a classe não herdar de Challenge
            ValueError: Se o tipo já estiver registado
        
        Example:
            >>> class CustomChallenge(Challenge):
            ...     pass
            >>> ChallengeFactory.register_challenge_type('custom', CustomChallenge)
            >>> 'custom' in ChallengeFactory.get_available_types()
            True
        """
        if not issubclass(challenge_class, Challenge):
            raise TypeError(
                f"A classe {challenge_class.__name__} deve herdar de Challenge"
            )
        
        if type_name in ChallengeFactory._challenge_types:
            raise ValueError(
                f"Tipo '{type_name}' já está registado. "
                f"Use um nome diferente ou remova o tipo existente primeiro."
            )
        
        ChallengeFactory._challenge_types[type_name] = challenge_class
    
    @staticmethod
    def unregister_challenge_type(type_name: str) -> None:
        """
        Remove um tipo de desafio do registro.
        
        Args:
            type_name: Nome do tipo a remover
        
        Raises:
            KeyError: Se o tipo não existir
        """
        if type_name not in ChallengeFactory._challenge_types:
            raise KeyError(f"Tipo '{type_name}' não está registado")
        
        del ChallengeFactory._challenge_types[type_name]
    
    @staticmethod
    def get_challenge_class(challenge_type: str) -> Optional[Type[Challenge]]:
        """
        Retorna a classe associada a um tipo sem instanciar.
        
        Útil para inspeção e testes.
        
        Args:
            challenge_type: Tipo do desafio
        
        Returns:
            Classe do desafio ou None se não existir
        """
        return ChallengeFactory._challenge_types.get(challenge_type)
    
    @staticmethod
    def create_challenge_set(animal_id: int, difficulty: int = 1) -> list[Challenge]:
        """
        Cria um conjunto completo de desafios para um animal.
        
        Útil para criar uma "ronda" de desafios variados.
        
        Args:
            animal_id: ID do animal
            difficulty: Nível de dificuldade
        
        Returns:
            Lista com um desafio de cada tipo disponível
        
        Example:
            >>> challenges = ChallengeFactory.create_challenge_set(animal_id=1)
            >>> len(challenges) == len(ChallengeFactory.get_available_types())
            True
        """
        return [
            ChallengeFactory.create_challenge(challenge_type, animal_id, difficulty)
            for challenge_type in ChallengeFactory._challenge_types.keys()
        ]


# Exemplo de uso (comentado - apenas para documentação)
if __name__ == "__main__":
    # Criar desafio específico
    audio_challenge = ChallengeFactory.create_challenge('audio', animal_id=1)
    print(f"Desafio criado: {audio_challenge}")
    print(f"Pergunta: {audio_challenge.get_question()}")
    
    # Criar desafio aleatório
    random_challenge = ChallengeFactory.create_random_challenge(animal_id=2)
    print(f"\nDesafio aleatório: {random_challenge}")
    
    # Listar tipos disponíveis
    print(f"\nTipos disponíveis: {ChallengeFactory.get_available_types()}")
    
    # Criar conjunto de desafios
    challenge_set = ChallengeFactory.create_challenge_set(animal_id=1)
    print(f"\nConjunto criado com {len(challenge_set)} desafios")
