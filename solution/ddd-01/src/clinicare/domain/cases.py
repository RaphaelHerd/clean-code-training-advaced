from dataclasses import dataclass, field
from datetime import datetime

from .events import CaseOpened, DomainEvent, MedicationPrescribed, new_event_id
from .exceptions import DomainError


@dataclass(frozen=True)
class MedicationOrder:
    # Value object: immutable, no identity. Two orders for the same medication
    # are equal by value — identical to comparing two integers.
    medication: str

@dataclass
class Case:
    case_id: str
    patient_id: str
    _is_open: bool = field(default=True, init=False)
    _medications: list[MedicationOrder] = field(default_factory=list[MedicationOrder], init=False, repr=False)
    _events: list[DomainEvent] = field(default_factory=list[DomainEvent], init=False, repr=False)

    @classmethod
    def open(cls, case_id: str, patient_id: str) -> "Case":
        # Factory method: every new Case starts in the open state.
        c = cls(case_id=case_id, patient_id=patient_id)
        c._events.append(
            CaseOpened(
                id=new_event_id(),
                occurred_at=datetime.utcnow(),
                case_id=case_id,
                patient_id=patient_id,
            )
        )
        return c

    def prescribe(self, medication: str) -> None:
        # Invariant: prescriptions require an open case.
        # Business rule lives here in the domain, not in the application layer.
        if not self._is_open:
            raise DomainError(f"Cannot prescribe to closed case '{self.case_id}'")
        
        self._medications.append(MedicationOrder(medication=medication))
        self._events.append(
            MedicationPrescribed(
                id=new_event_id(),
                occurred_at=datetime.utcnow(),
                case_id=self.case_id,
                medication=medication,
            )
        )

    def close(self) -> None:
        # Invariant: closing an already-closed case is an error.
        if not self._is_open:
            raise DomainError(f"Case '{self.case_id}' is already closed")
        
        self._is_open = False

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def medications(self) -> list[MedicationOrder]:
        # defensive copy — callers cannot mutate internals
        return list(self._medications)

    def pull_events(self) -> list[DomainEvent]:
        ev, self._events = self._events, []
        return ev
