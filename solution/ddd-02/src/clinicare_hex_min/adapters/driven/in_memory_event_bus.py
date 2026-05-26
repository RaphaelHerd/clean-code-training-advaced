from typing import Callable, Dict, List, Type, TypeVar, cast
from clinicare_hex_min.core.domain.events import DomainEvent

TEvent = TypeVar("TEvent", bound=DomainEvent)
EventHandler = Callable[[DomainEvent], None]

class SimpleEventBus:
    def __init__(self) -> None:
        self._subs: Dict[Type[DomainEvent], List[EventHandler]] = {}

    def subscribe(
        self, event_type: Type[TEvent], handler: Callable[[TEvent], None]
    ) -> None:
        # setdefault creates an empty list the first time a type is registered,
        # then appends the handler.  Multiple handlers per type are fully supported.
        self._subs.setdefault(event_type, []).append(cast(EventHandler, handler))

    def publish(self, event: DomainEvent) -> None:
        # isinstance allows subclass events to match parent-type subscriptions.
        # For example, a handler subscribed to DomainEvent would receive every event.
        for event_type, handlers in self._subs.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    # Call the handler synchronously.  In production you might
                    # push to a queue instead, but in-memory is correct here.
                    handler(event)