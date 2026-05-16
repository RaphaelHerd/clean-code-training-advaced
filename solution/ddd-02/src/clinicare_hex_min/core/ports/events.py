from typing import Protocol
from clinicare_hex_min.core.domain.events import DomainEvent

class EventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
