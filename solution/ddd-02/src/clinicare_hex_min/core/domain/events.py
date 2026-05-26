from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class DomainEvent:
    id: str
    occurred_at: datetime


@dataclass(frozen=True)
class PatientRegistered(DomainEvent):
    patient_id: str


def new_event_id() -> str:
    return str(uuid.uuid4())
