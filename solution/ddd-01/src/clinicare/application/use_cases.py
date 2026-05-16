from datetime import date

from clinicare.domain.cases import Case
from clinicare.domain.exceptions import DomainError
from clinicare.domain.patients import Patient
from clinicare.application.event_publisher import EventPublisher
from clinicare.application.repositories import CaseRepository, PatientRepository


class RegisterPatient:
    def __init__(self, patient_repo: PatientRepository, bus: EventPublisher) -> None:
        self._patient_repo = patient_repo
        self._bus = bus

    def __call__(self, patient_id: str, name: str, dob: date) -> Patient:
        # Precondition: the patient must not already exist.
        if self._patient_repo.get(patient_id):
            raise DomainError(f"Patient '{patient_id}' already exists")

        # Domain creates the aggregate — the use case never sets fields directly.
        patient = Patient.register(patient_id, name, dob)
        self._patient_repo.save(patient)

        # Publish events only after successful persistence.
        # If save() raised an exception above, no phantom events would be emitted.
        for event in patient.pull_events():
            self._bus.publish(event)

        return patient


class OpenCase:
    def __init__(
        self,
        patient_repo: PatientRepository,
        case_repo: CaseRepository,
        bus: EventPublisher,
    ) -> None:
        self._patient_repo = patient_repo
        self._case_repo = case_repo
        self._bus = bus

    def __call__(self, case_id: str, patient_id: str) -> Case:
        # Cross-aggregate check: the patient must exist before a case can be opened.
        if not self._patient_repo.get(patient_id):
            raise DomainError(f"Patient '{patient_id}' not found")

        case = Case.open(case_id, patient_id)
        self._case_repo.save(case)

        for event in case.pull_events():
            self._bus.publish(event)

        return case


class PrescribeMedication:
    def __init__(self, case_repo: CaseRepository, bus: EventPublisher) -> None:
        self._case_repo = case_repo
        self._bus = bus

    def __call__(self, case_id: str, medication: str) -> None:
        case = self._case_repo.get(case_id)
        if not case:
            raise DomainError(f"Case '{case_id}' not found")

        # Domain enforces the invariant (case must be open) — not this use case.
        case.prescribe(medication)
        self._case_repo.save(case)

        for event in case.pull_events():
            self._bus.publish(event)


class CloseCase:
    def __init__(self, case_repo: CaseRepository, bus: EventPublisher) -> None:
        self._case_repo = case_repo
        self._bus = bus

    def __call__(self, case_id: str) -> None:
        case = self._case_repo.get(case_id)
        if not case:
            raise DomainError(f"Case '{case_id}' not found")

        # Domain enforces the invariant (cannot close twice) — not this use case.
        case.close()
        self._case_repo.save(case)

        for event in case.pull_events():
            self._bus.publish(event)
