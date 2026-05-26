from dataclasses import dataclass, field
from datetime import date, datetime

from .events import DomainEvent, PatientRegistered, new_event_id
from .exceptions import DomainError


@dataclass(frozen=True)
class PatientId:
    value: str


@dataclass
class Patient:
    patient_id: PatientId
    name: str
    date_of_birth: date
    
    # Transient event buffer — not part of the public interface.
    # Field is excluded from __init__ and __repr__ to keep it invisible.
    _events: list[DomainEvent] = field(default_factory=list[DomainEvent], init=False, repr=False)

    def __post_init__(self) -> None:
        # Invariant: a patient cannot be born in the future.
        if self.date_of_birth >= date.today():
            raise DomainError("Date of birth must be in the past")
        # Invariant: every patient must have a non-empty name.
        if not self.name or not self.name.strip():
            raise DomainError("Patient name must not be empty")

    @classmethod
    def register(cls, patient_id: str, name: str, dob: date) -> "Patient":
        # Factory method keeps construction and first-event emission together.
        # Callers never call the constructor directly — they always use register().
        p = cls(patient_id=PatientId(patient_id), name=name, date_of_birth=dob)
        # Buffer the event — do NOT publish here.  The application layer drains
        # the buffer only after the aggregate has been persisted successfully,
        # preventing ghost events if persistence fails.
        p._events.append(
            PatientRegistered(
                id=new_event_id(),
                occurred_at=datetime.utcnow(),
                patient_id=patient_id,
            )
        )
        return p

    def pull_events(self) -> list[DomainEvent]:
        # Atomic swap: copy the buffer, reset it, return the copy.
        # This guarantees no event is published twice even under concurrent calls.
        ev, self._events = self._events, []
        return ev
