from typing import Dict, Optional, Union

from clinicare.domain.cases import Case
from clinicare.domain.patients import Patient, PatientId


class InMemoryPatientRepository:
    def __init__(self) -> None:
        self._store: Dict[str, Patient] = {}

    def get(self, patient_id: Union[str, PatientId]) -> Optional[Patient]:
        key = patient_id.value if isinstance(patient_id, PatientId) else patient_id
        return self._store.get(key)

    def save(self, patient: Patient) -> None:
        self._store[patient.patient_id.value] = patient


class InMemoryCaseRepository:
    def __init__(self) -> None:
        self._store: Dict[str, Case] = {}

    def get(self, case_id: str) -> Optional[Case]:
        return self._store.get(case_id)

    def save(self, case: Case) -> None:
        self._store[case.case_id] = case
