"""
Classe abstrata base para todos os desafios do jogo.

Padrões Implementados:
- Factory Method (Criacional): Produto Abstrato
- Observer (Comportamental): Subject/Observable

Autores: Henrique Crachat (2501450) & Fábio Amado (2501444)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from observers.challenge_observer import ChallengeObserver


class Challenge(ABC):
    """
    Classe base abstrata para desafios do jogo "Dia & Noite".

    Define a interface que todos os desafios concretos devem implementar.
    Esta é a classe "Produto" no padrão Factory Method e "Subject" no Observer.

    Padrão Observer:
    - Subject: Esta classe mantém lista de observers e os notifica de eventos
    - Observers podem se registar para receber notificações sobre:
      * Desafio iniciado
      * Desafio completado
      * Desafio pulado

    Attributes:
        animal_id (int): ID do animal relacionado ao desafio
        difficulty (int): Nível de dificuldade (1-5)
        challenge_id (str): Identificador único do desafio
        correct_answer (str): Resposta correta do desafio
        _observers (List[ChallengeObserver]): Lista de observers registados
    """

    def __init__(self, animal_id: int, difficulty: int = 1):
        """
        Inicializa um desafio.

        Args:
            animal_id: ID do animal para este desafio
            difficulty: Nível de dificuldade (padrão: 1)
        """
        self.animal_id = animal_id
        self.difficulty = difficulty
        self.challenge_id = None
        self.correct_answer = None

        # Padrão Observer: Lista de observers
        self._observers: List['ChallengeObserver'] = []
    
    @abstractmethod
    def get_question(self) -> str:
        """
        Retorna a pergunta do desafio.
        
        Returns:
            String com a pergunta a apresentar ao aluno
        """
        pass
    
    @abstractmethod
    def get_options(self) -> List[str]:
        """
        Retorna as opções de resposta.
        
        Returns:
            Lista com as opções de resposta (incluindo a correta)
        """
        pass
    
    @abstractmethod
    def get_challenge_type(self) -> str:
        """
        Retorna o tipo do desafio.
        
        Returns:
            String identificando o tipo ('audio', 'visual', etc.)
        """
        pass
    
    @abstractmethod
    def validate_answer(self, answer: str) -> bool:
        """
        Valida se a resposta do aluno está correta.
        
        Args:
            answer: Resposta fornecida pelo aluno
            
        Returns:
            True se a resposta está correta, False caso contrário
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o desafio para formato dicionário (JSON).

        Returns:
            Dicionário com todos os dados do desafio
        """
        return {
            'challenge_id': self.challenge_id,
            'animal_id': self.animal_id,
            'type': self.get_challenge_type(),
            'difficulty': self.difficulty,
            'question': self.get_question(),
            'options': self.get_options()
        }

    # ========== Métodos do Padrão Observer ==========

    def attach(self, observer: 'ChallengeObserver') -> None:
        """
        Anexa um observer para receber notificações deste desafio.

        Padrão Observer: Permite que observers se registem para receber
        notificações quando eventos ocorrem.

        Args:
            observer: Observer a ser anexado
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: 'ChallengeObserver') -> None:
        """
        Remove um observer da lista de notificações.

        Args:
            observer: Observer a ser removido
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_started(self, user_id: str) -> None:
        """
        Notifica todos os observers que o desafio foi iniciado.

        Args:
            user_id: ID do utilizador que iniciou o desafio
        """
        for observer in self._observers:
            observer.on_challenge_started(user_id, self)

    def notify_completed(self, user_id: str, answer: str,
                        time_taken: float, is_correct: bool) -> None:
        """
        Notifica todos os observers que o desafio foi completado.

        Args:
            user_id: ID do utilizador
            answer: Resposta fornecida
            time_taken: Tempo decorrido em segundos
            is_correct: Se a resposta está correta
        """
        for observer in self._observers:
            observer.on_challenge_completed(user_id, self, answer,
                                           time_taken, is_correct)

    def notify_skipped(self, user_id: str) -> None:
        """
        Notifica todos os observers que o desafio foi pulado.

        Args:
            user_id: ID do utilizador
        """
        for observer in self._observers:
            observer.on_challenge_skipped(user_id, self)

    # ================================================

    def __repr__(self) -> str:
        """Representação em string do desafio"""
        return f"{self.__class__.__name__}(animal_id={self.animal_id}, difficulty={self.difficulty})"
