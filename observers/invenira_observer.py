"""
Inven!RA Observer - Observer Concreto para Integração com Plataforma Inven!RA

Implementa o padrão Observer para notificar a plataforma Inven!RA
sobre eventos e progresso dos estudantes.

Padrão: Observer (Comportamental)
Papel: ConcreteObserver
"""

from observers.challenge_observer import ChallengeObserver
from typing import Dict, Optional
from datetime import datetime
import json


class InveniraObserver(ChallengeObserver):
    """
    Observer responsável por comunicar com a plataforma Inven!RA.

    Envia notificações de eventos para a plataforma externa,
    permitindo tracking e integração com outros sistemas educacionais.
    """

    def __init__(self, platform_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Inicializa o observer de Inven!RA.

        Args:
            platform_url: URL da API da plataforma Inven!RA
            api_key: Chave de API para autenticação
        """
        self.platform_url = platform_url or "https://api.invenira.pt/v1"
        self.api_key = api_key
        self.event_queue = []  # Fila de eventos para envio em batch
        self.max_queue_size = 10

    def on_challenge_completed(self, user_id: str, challenge, answer: str,
                               time_taken: float, is_correct: bool) -> None:
        """
        Notifica Inven!RA quando um desafio é completado.

        Args:
            user_id: Identificador do usuário (inveniraStdID)
            challenge: Instância do desafio completado
            answer: Resposta fornecida
            time_taken: Tempo decorrido em segundos
            is_correct: Se a resposta está correta
        """
        event = {
            'event_type': 'challenge_completed',
            'timestamp': datetime.now().isoformat(),
            'student_id': user_id,
            'activity_id': 'dia-noite-animals',
            'challenge_data': {
                'type': challenge.get_challenge_type(),
                'difficulty': getattr(challenge, 'difficulty', 'medium'),
                'animal_id': getattr(challenge, 'animal_id', None),
                'is_correct': is_correct,
                'time_taken': time_taken,
                'answer_given': answer
            },
            'metadata': {
                'session_id': self._generate_session_id(user_id),
                'device': 'web',
                'version': '1.0.0'
            }
        }

        self._queue_event(event)

        result_text = "CORRECT" if is_correct else "INCORRECT"
        print(f"[InveniraObserver] Notificacao enviada para Inven!RA - "
              f"Student: {user_id}, Result: {result_text}")

    def on_challenge_started(self, user_id: str, challenge) -> None:
        """
        Notifica Inven!RA quando um desafio é iniciado.

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio iniciado
        """
        event = {
            'event_type': 'challenge_started',
            'timestamp': datetime.now().isoformat(),
            'student_id': user_id,
            'activity_id': 'dia-noite-animals',
            'challenge_data': {
                'type': challenge.get_challenge_type(),
                'difficulty': getattr(challenge, 'difficulty', 'medium'),
                'animal_id': getattr(challenge, 'animal_id', None)
            }
        }

        self._queue_event(event)

        print(f"[InveniraObserver] Desafio iniciado notificado - "
              f"Student: {user_id}, Type: {challenge.get_challenge_type()}")

    def on_challenge_skipped(self, user_id: str, challenge) -> None:
        """
        Notifica Inven!RA quando um desafio é pulado.

        Args:
            user_id: Identificador do usuário
            challenge: Instância do desafio pulado
        """
        event = {
            'event_type': 'challenge_skipped',
            'timestamp': datetime.now().isoformat(),
            'student_id': user_id,
            'activity_id': 'dia-noite-animals',
            'challenge_data': {
                'type': challenge.get_challenge_type(),
                'animal_id': getattr(challenge, 'animal_id', None)
            }
        }

        self._queue_event(event)

    def notify_level_up(self, user_id: str, new_level: int, metrics: Dict) -> None:
        """
        Notifica Inven!RA quando estudante sobe de nível.

        Args:
            user_id: Identificador do usuário
            new_level: Novo nível alcançado
            metrics: Métricas associadas ao level up
        """
        event = {
            'event_type': 'level_up',
            'timestamp': datetime.now().isoformat(),
            'student_id': user_id,
            'activity_id': 'dia-noite-animals',
            'level_data': {
                'new_level': new_level,
                'total_challenges': metrics.get('total_challenges', 0),
                'accuracy_rate': metrics.get('accuracy_rate', 0)
            }
        }

        self._queue_event(event)

        print(f"[InveniraObserver] Level Up notificado - "
              f"Student: {user_id}, Level: {new_level}")

    def notify_achievement(self, user_id: str, achievement_id: str,
                          achievement_name: str) -> None:
        """
        Notifica Inven!RA quando estudante desbloqueia conquista.

        Args:
            user_id: Identificador do usuário
            achievement_id: ID da conquista
            achievement_name: Nome da conquista
        """
        event = {
            'event_type': 'achievement_unlocked',
            'timestamp': datetime.now().isoformat(),
            'student_id': user_id,
            'activity_id': 'dia-noite-animals',
            'achievement_data': {
                'achievement_id': achievement_id,
                'achievement_name': achievement_name
            }
        }

        self._queue_event(event)

        print(f"[InveniraObserver] Achievement notificado - "
              f"Student: {user_id}, Achievement: {achievement_name}")

    def send_progress_report(self, user_id: str, progress_data: Dict) -> None:
        """
        Envia relatório de progresso completo para Inven!RA.

        Args:
            user_id: Identificador do usuário
            progress_data: Dados de progresso do utilizador
        """
        event = {
            'event_type': 'progress_report',
            'timestamp': datetime.now().isoformat(),
            'student_id': user_id,
            'activity_id': 'dia-noite-animals',
            'report_data': progress_data
        }

        self._send_event(event)

        print(f"[InveniraObserver] Relatorio de progresso enviado - "
              f"Student: {user_id}")

    def _queue_event(self, event: Dict) -> None:
        """
        Adiciona evento à fila e envia em batch se atingir limite.

        Args:
            event: Dados do evento
        """
        self.event_queue.append(event)

        # Se atingir limite, enviar batch
        if len(self.event_queue) >= self.max_queue_size:
            self._flush_queue()

    def _flush_queue(self) -> None:
        """Envia todos os eventos na fila para Inven!RA."""
        if not self.event_queue:
            return

        # Em produção, enviaria via HTTP POST para a API
        # Por agora, simula o envio
        print(f"[InveniraObserver] Enviando batch de {len(self.event_queue)} eventos")

        # Simulação de envio (em produção usaria requests.post)
        batch_payload = {
            'events': self.event_queue,
            'batch_timestamp': datetime.now().isoformat(),
            'api_key': self.api_key
        }

        # Logging para debugging (em produção removeria)
        if False:  # Mudar para True para debug detalhado
            print(json.dumps(batch_payload, indent=2))

        # Limpar fila após envio
        self.event_queue = []

    def _send_event(self, event: Dict) -> None:
        """
        Envia evento individual imediatamente para Inven!RA.

        Args:
            event: Dados do evento
        """
        # Em produção, enviaria via HTTP POST
        print(f"[InveniraObserver] Enviando evento: {event['event_type']}")

        # Simulação de envio (em produção usaria requests.post)
        # response = requests.post(
        #     f"{self.platform_url}/events",
        #     json=event,
        #     headers={'Authorization': f'Bearer {self.api_key}'}
        # )

    def _generate_session_id(self, user_id: str) -> str:
        """
        Gera ID de sessão para tracking.

        Args:
            user_id: Identificador do usuário

        Returns:
            Session ID único
        """
        from hashlib import md5
        timestamp = datetime.now().isoformat()
        session_data = f"{user_id}_{timestamp}"
        return md5(session_data.encode()).hexdigest()[:16]

    def get_pending_events(self) -> int:
        """
        Retorna número de eventos pendentes na fila.

        Returns:
            Quantidade de eventos não enviados
        """
        return len(self.event_queue)

    def force_flush(self) -> None:
        """Força envio de todos os eventos pendentes."""
        self._flush_queue()
