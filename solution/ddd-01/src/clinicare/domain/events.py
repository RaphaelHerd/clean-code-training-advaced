from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class DomainEvent:
    id: str
    occurred_at: datetime
    
# Each concrete event carries only the identifiers that downstream consumers
# need to do their job.  Sensitive fields (patient names, medication dosages)
# are intentionally excluded — events cross context boundaries and must not
# leak private data.

@dataclass(frozen=True)
class PatientRegistered(DomainEvent):
    patient_id: str


@dataclass(frozen=True)
class CaseOpened(DomainEvent):
    case_id: str
    patient_id: str


@dataclass(frozen=True)
class MedicationPrescribed(DomainEvent):
    case_id: str
    medication: str

def new_event_id() -> str:
    return str(uuid.uuid4())
