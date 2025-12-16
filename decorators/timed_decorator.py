"""
TimedChallengeDecorator - Adiciona limite de tempo aos desafios.

Padrão de Estrutura: Decorator (Concrete Decorator)

Autores: Henrique Crachat (2501450) & Fábio Amado (2501444)
UC: Arquitetura e Padrões de Software
Universidade Aberta
"""
from decorators.challenge_decorator import ChallengeDecorator
from models.challenge import Challenge
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class TimedChallengeDecorator(ChallengeDecorator):
    """
    Decorator que adiciona limite de tempo a um Challenge.

    PADRÃO: Concrete Decorator

    Funcionalidades Adicionadas:
    ---------------------------
    1. Limite de tempo configurável (segundos)
    2. Tracking de tempo decorrido
    3. Validação automática de timeout
    4. Metadata temporal no to_dict()
    5. Mensagens de pressão de tempo na pergunta

    Use Cases:
    ----------------------
    - Desafios de nível avançado com pressão de tempo
    - Testes rápidos de conhecimento
    - Gamificação com bônus por rapidez
    - Simulação de situações de pressão

    """

    def __init__(self,
                 challenge: Challenge,
                 time_limit_seconds: int = 30,
                 show_timer_in_question: bool = True):
        """
        Inicializa o decorator com limite de tempo.

        Args:
            challenge: Challenge a ser decorado
            time_limit_seconds: Tempo limite em segundos (padrão: 30)
            show_timer_in_question: Mostrar indicador de tempo na pergunta
        """
        super().__init__(challenge)
        self.time_limit_seconds = time_limit_seconds
        self.start_time: Optional[datetime] = None
        self.show_timer_in_question = show_timer_in_question
        self._end_time: Optional[datetime] = None
        self._answer_submitted: bool = False

    def start_timer(self) -> None:
        """
        Inicia a contagem do tempo.

        Deve ser chamado quando o desafio é apresentado ao aluno.
        """
        self.start_time = datetime.now()
        self._end_time = None
        self._answer_submitted = False

    def get_elapsed_time(self) -> float:
        """
        Retorna tempo decorrido em segundos.

        Returns:
            Tempo em segundos desde start_timer(), ou 0 se não iniciado
        """
        if self.start_time is None:
            return 0.0

        end_point = self._end_time if self._end_time else datetime.now()
        elapsed = (end_point - self.start_time).total_seconds()
        return round(elapsed, 2)

    def get_remaining_time(self) -> float:
        """
        Retorna tempo restante em segundos.

        Returns:
            Tempo restante, ou 0 se timeout ou não iniciado
        """
        if self.start_time is None:
            return float(self.time_limit_seconds)

        elapsed = self.get_elapsed_time()
        remaining = self.time_limit_seconds - elapsed
        return max(0.0, round(remaining, 2))

    def is_timed_out(self) -> bool:
        """
        Verifica se o tempo limite foi excedido.

        Returns:
            True se timeout, False caso contrário
        """
        if self.start_time is None:
            return False

        return self.get_elapsed_time() > self.time_limit_seconds

    def get_question(self) -> str:
        """
        Retorna pergunta com indicador de tempo.

        Adiciona emoji de relógio e tempo limite à pergunta original.

        Returns:
            Pergunta decorada com informação temporal
        """
        base_question = super().get_question()

        if self.show_timer_in_question:
            return f"[{self.time_limit_seconds}s] {base_question}"

        return base_question

    def validate_answer(self, answer: str) -> bool:
        """
        Valida resposta verificando timeout.

        IMPORTANTE: Este método verifica apenas correção.
        Use validate_answer_with_timing() para informação completa.

        Args:
            answer: Resposta do aluno

        Returns:
            False se timeout OU resposta incorreta, True se correto e no tempo
        """
        # Marcar submissão
        if not self._answer_submitted:
            self._end_time = datetime.now()
            self._answer_submitted = True

        # Se timeout, resposta é automaticamente incorreta
        if self.is_timed_out():
            return False

        # Validar resposta normalmente
        return super().validate_answer(answer)

    def validate_answer_with_timing(self, answer: str) -> Dict[str, Any]:
        """
        Valida resposta e retorna informação temporal completa.

        Este é o método recomendado para uso com TimedChallenge.
        Fornece contexto completo sobre timing e correção.

        Args:
            answer: Resposta do aluno

        Returns:
            Dicionário com:
                - is_correct (bool): Se a resposta está correta
                - time_taken (float): Tempo gasto em segundos
                - timed_out (bool): Se houve timeout
                - time_remaining (float): Tempo restante quando respondeu
                - time_limit (int): Limite de tempo configurado
                - correct_answer (str): Resposta correta (se errou)
        """
        # Marcar tempo de submissão
        if not self._answer_submitted:
            self._end_time = datetime.now()
            self._answer_submitted = True

        time_taken = self.get_elapsed_time()
        timed_out = self.is_timed_out()
        time_remaining = self.get_remaining_time()

        # Validar resposta
        is_correct = super().validate_answer(answer) if not timed_out else False

        result = {
            'is_correct': is_correct,
            'time_taken': time_taken,
            'timed_out': timed_out,
            'time_remaining': time_remaining,
            'time_limit': self.time_limit_seconds
        }

        # Adicionar resposta correta se errou
        if not is_correct:
            result['correct_answer'] = self.correct_answer
            if timed_out:
                result['timeout_message'] = f"Tempo esgotado! Limite: {self.time_limit_seconds}s"

        return result

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa para JSON incluindo metadados temporais.

        Returns:
            Dicionário com dados do challenge + informação temporal
        """
        base_dict = super().to_dict()

        # Adicionar metadados de timing
        base_dict.update({
            'timed': True,
            'time_limit_seconds': self.time_limit_seconds,
            'timer_started': self.start_time is not None,
            'time_elapsed': self.get_elapsed_time() if self.start_time else 0,
            'time_remaining': self.get_remaining_time(),
            'is_timed_out': self.is_timed_out()
        })

        return base_dict

    def reset_timer(self) -> None:
        """
        Reseta o timer para permitir nova tentativa.

        Útil para modo de prática ou segunda tentativa.
        """
        self.start_time = None
        self._end_time = None
        self._answer_submitted = False

    def get_time_pressure_level(self) -> str:
        """
        Retorna nível de pressão de tempo baseado no tempo restante.

        Útil para UI/UX adaptativa (cores, alertas, etc).

        Returns:
            'low', 'medium', 'high', ou 'critical'
        """
        if self.start_time is None:
            return 'none'

        remaining = self.get_remaining_time()
        percentage_remaining = (remaining / self.time_limit_seconds) * 100

        if percentage_remaining > 50:
            return 'low'
        elif percentage_remaining > 25:
            return 'medium'
        elif percentage_remaining > 10:
            return 'high'
        else:
            return 'critical'

    def __repr__(self) -> str:
        """Representação em string com informação de timing"""
        return f"TimedChallengeDecorator({self.time_limit_seconds}s, {self._challenge})"


# =====================================================
# EXEMPLO DE USO
# =====================================================
if __name__ == "__main__":
    """
    Demonstração de uso do TimedChallengeDecorator.

    Este exemplo mostra:
    1. Integração com Factory Method
    2. Decoração de challenge
    3. Uso de timing
    4. Combinação potencial com outros decorators
    """
    from factories.challenge_factory import ChallengeFactory
    import time

    print("=== Demonstração TimedChallengeDecorator ===\n")

    # 1. Criar challenge base com Factory Method
    print("1. Criando challenge base com Factory Method...")
    base_challenge = ChallengeFactory.create_challenge('audio', animal_id=1, difficulty=1)
    print(f"   Challenge criado: {base_challenge}")
    print(f"   Pergunta original: {base_challenge.get_question()}\n")

    # 2. Decorar com timing
    print("2. Decorando com TimedChallengeDecorator...")
    timed_challenge = TimedChallengeDecorator(
        challenge=base_challenge,
        time_limit_seconds=10
    )
    print(f"   Challenge decorado: {timed_challenge}")
    print(f"   Pergunta com timer: {timed_challenge.get_question()}\n")

    # 3. Iniciar timer e simular resposta
    print("3. Iniciando timer...")
    timed_challenge.start_timer()
    print(f"   Timer iniciado!")

    # Simular pensamento (3 segundos)
    time.sleep(3)

    print(f"   Tempo decorrido: {timed_challenge.get_elapsed_time()}s")
    print(f"   Tempo restante: {timed_challenge.get_remaining_time()}s")
    print(f"   Pressão: {timed_challenge.get_time_pressure_level()}\n")

    # 4. Validar resposta com timing
    print("4. Validando resposta com timing...")
    result = timed_challenge.validate_answer_with_timing("Leão")
    print(f"   Resultado completo:")
    for key, value in result.items():
        print(f"   - {key}: {value}")

    print("\n5. Serialização JSON:")
    import json
    print(json.dumps(timed_challenge.to_dict(), indent=2))
