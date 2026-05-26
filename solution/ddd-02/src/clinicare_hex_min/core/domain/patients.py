from dataclasses import dataclass, field
from datetime import date, datetime
from .exceptions import DomainError
from .events import DomainEvent, PatientRegistered, new_event_id


@dataclass(frozen=True)
class PatientId:
    value: str


@dataclass
class Patient:
    patient_id: PatientId
    name: str
    date_of_birth: date
    _events: list[DomainEvent] = field(default_factory=list[DomainEvent], init=False, repr=False)

    def __post_init__(self) -> None:
        if self.date_of_birth >= date.today():
            raise DomainError("Date of birth must be in the past")

    @classmethod
    def register(cls, pid: str, name: str, dob: date, at: datetime) -> "Patient":
        p = cls(patient_id=PatientId(pid), name=name, date_of_birth=dob)
        p._events.append(
            PatientRegistered(
                id=new_event_id(),
                occurred_at=at,
                patient_id=pid,
            )
        )
        return p

    def pull_events(self) -> list[DomainEvent]:
        ev, self._events = self._events, []
        return ev
