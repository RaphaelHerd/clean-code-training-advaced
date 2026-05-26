from typing import Optional, Protocol, Union
from clinicare.domain.cases import Case
from clinicare.domain.patients import Patient, PatientId

class PatientRepository(Protocol):
    def get(self, patient_id: Union[str, PatientId]) -> Optional[Patient]: ...

    def save(self, patient: Patient) -> None: ...


class CaseRepository(Protocol):
    def get(self, case_id: str) -> Optional[Case]: ...

    def save(self, case: Case) -> None: ...