from typing import Callable, Dict, List, Set, Tuple, Type, TypeVar, cast

from clinicare.domain.events import DomainEvent, MedicationPrescribed


TEvent = TypeVar("TEvent", bound=DomainEvent)
EventHandler = Callable[[DomainEvent], None]


class EventBus:
    def __init__(self) -> None:
        # Maps event class → list of handler callables.
        # A dict of lists is the simplest pub/sub structure possible.
        self._handlers: Dict[Type[object], List[EventHandler]] = {}

    def subscribe(
        self, event_type: Type[TEvent], handler: Callable[[TEvent], None]
    ) -> None:
        # Register a handler callable for a specific event type.
        # setdefault initialises the list on the first subscription for that type.
        self._handlers.setdefault(event_type, []).append(cast(EventHandler, handler))

    def publish(self, event: DomainEvent) -> None:
        # Deliver the event to every handler whose subscribed type matches.
        # isinstance allows a handler subscribed to DomainEvent to receive all
        # concrete event subtypes — useful for catch-all logging handlers.
        for event_type, handlers in self._handlers.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    handler(event)


def duplicate_medication_alert(
    seen: Set[Tuple[str, str]]
) -> Callable[[MedicationPrescribed], None]:
    """Returns a handler that warns when the same medication appears twice."""
    def handler(event: MedicationPrescribed) -> None:
        key = (event.case_id, event.medication)
        if key in seen:
            print(f"ALERT: '{event.medication}' prescribed twice in case '{event.case_id}'")
        seen.add(key)

    return handler
