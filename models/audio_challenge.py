"""
Desafio de reconhecimento auditivo.

Padrão de Criação: Factory Method (Produto Concreto)

ANTI-PADRÃO CORRIGIDO: Circular Import
Anteriormente, imports estavam dentro de __init__ para evitar dependência circular.
Agora usa import do módulo no topo, seguindo boas práticas Python.

Autores: Henrique Crachat (2501450)
"""
from models.challenge import Challenge
from typing import List
import random
from data import animals_data


class AudioChallenge(Challenge):
    """
    Desafio baseado no som do animal.
    
    O aluno ouve um som de animal e deve identificá-lo entre várias opções.
    Este é um "Produto Concreto" no padrão Factory Method.
    
    Example:
        >>> challenge = AudioChallenge(animal_id=1)
        >>> print(challenge.get_question())
        "Que animal produz este som?"
    """
    
    def __init__(self, animal_id: int, difficulty: int = 1):
        """
        Inicializa desafio auditivo.

        Args:
            animal_id: ID do animal
            difficulty: Nível de dificuldade
        """
        super().__init__(animal_id, difficulty)

        self.animal_data = animals_data.get_animal_data(animal_id)
        self.challenge_id = f"audio_{animal_id}_{random.randint(1000, 9999)}"
        self.correct_answer = self.animal_data['name_pt']
        self.audio_file = self.animal_data['sound_file']

        # Gerar opções de resposta
        self._generate_options = lambda: self._create_options(animals_data.get_random_animals)
    
    def _create_options(self, get_random_animals_func) -> List[str]:
        """Gera opções de resposta com distratores"""
        similar_animals = get_random_animals_func(
            habitat=self.animal_data['habitat'],
            exclude_id=self.animal_id,
            count=3
        )
        
        options = [self.correct_answer] + [a['name_pt'] for a in similar_animals]
        random.shuffle(options)
        return options
    
    def get_question(self) -> str:
        """Retorna a pergunta do desafio"""
        return "Que animal produz este som?"
    
    def get_options(self) -> List[str]:
        """Retorna as opções de resposta"""
        return self._generate_options()
    
    def get_challenge_type(self) -> str:
        """Retorna o tipo do desafio"""
        return "audio"
    
    def validate_answer(self, answer: str) -> bool:
        """
        Valida a resposta do aluno.
        
        Args:
            answer: Resposta fornecida
            
        Returns:
            True se correto
        """
        return answer.strip().lower() == self.correct_answer.lower()
    
    def to_dict(self):
        """Converte para dicionário incluindo ficheiro de áudio"""
        data = super().to_dict()
        data['audio_file'] = self.audio_file
        data['instructions'] = "Clica no ícone 🔊 para ouvir o som do animal"
        return data
