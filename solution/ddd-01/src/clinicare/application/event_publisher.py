from typing import Protocol
from clinicare.domain.events import DomainEvent

class EventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None: ...