from typing import Dict, Optional

from clinicare_hex_min.core.domain.patients import Patient, PatientId


class InMemoryPatientRepository:
    def __init__(self) -> None:
        self._store: Dict[str, Patient] = {}

    def get(self, pid: PatientId) -> Optional[Patient]:
        # pid.value is the plain string identifier (e.g. "p1").
        # dict.get() returns None automatically when the key is absent,
        # so callers can check `if repo.get(pid)` without catching exceptions.
        return self._store.get(pid.value)

    def save(self, patient: Patient) -> None:
        # Overwrite any existing entry — this acts as both insert and update.
        # In a real repository this would call an ORM or execute a SQL UPSERT.
        self._store[patient.patient_id.value] = patient
