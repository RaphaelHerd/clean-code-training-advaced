from datetime import date

import pytest

from clinicare.application.use_cases import (
    CloseCase,
    OpenCase,
    PrescribeMedication,
    RegisterPatient,
)
from clinicare.domain.events import (
    CaseOpened,
    DomainEvent,
    MedicationPrescribed,
    PatientRegistered,
)
from clinicare.domain.exceptions import DomainError
from clinicare.domain.patients import Patient
from clinicare.infrastructure.event_bus import EventBus, duplicate_medication_alert
from clinicare.infrastructure.projections import ReportingProjection
from clinicare.infrastructure.repositories import (
    InMemoryCaseRepository,
    InMemoryPatientRepository,
)


class SpyBus:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.events.append(event)


class FailingPatientRepository(InMemoryPatientRepository):
    def save(self, patient: Patient) -> None:
        raise RuntimeError("database unavailable")


def test_register_patient_prevents_duplicates() -> None:
    repo = InMemoryPatientRepository()
    bus = SpyBus()
    register = RegisterPatient(repo, bus)

    register("p1", "Alice", date(1990, 5, 2))

    with pytest.raises(DomainError, match="already exists"):
        register("p1", "Alice", date(1990, 5, 2))


def test_register_patient_publishes_only_after_successful_save() -> None:
    repo = FailingPatientRepository()
    bus = SpyBus()
    register = RegisterPatient(repo, bus)

    with pytest.raises(RuntimeError, match="database unavailable"):
        register("p1", "Alice", date(1990, 5, 2))

    assert bus.events == []


def test_open_case_requires_existing_patient() -> None:
    patient_repo = InMemoryPatientRepository()
    case_repo = InMemoryCaseRepository()
    bus = SpyBus()
    open_case = OpenCase(patient_repo, case_repo, bus)

    with pytest.raises(DomainError, match="not found"):
        open_case("c1", "missing")


def test_full_flow_updates_reporting_projection_and_alerts_on_duplicate(
    capsys: pytest.CaptureFixture[str],
) -> None:
    patient_repo = InMemoryPatientRepository()
    case_repo = InMemoryCaseRepository()
    bus = EventBus()
    reporting = ReportingProjection()
    published_events: list[DomainEvent] = []

    bus.subscribe(DomainEvent, published_events.append)
    bus.subscribe(PatientRegistered, reporting.on_patient_registered)
    bus.subscribe(CaseOpened, reporting.on_case_opened)
    bus.subscribe(MedicationPrescribed, reporting.on_medication_prescribed)
    bus.subscribe(MedicationPrescribed, duplicate_medication_alert(set()))

    register = RegisterPatient(patient_repo, bus)
    open_case = OpenCase(patient_repo, case_repo, bus)
    prescribe = PrescribeMedication(case_repo, bus)
    close_case = CloseCase(case_repo, bus)

    patient = register("p1", "Alice", date(1990, 5, 2))
    case = open_case("c1", patient.patient_id.value)
    prescribe(case.case_id, "Amoxicillin")
    prescribe(case.case_id, "Amoxicillin")
    close_case(case.case_id)

    captured = capsys.readouterr()
    assert "ALERT: 'Amoxicillin' prescribed twice in case 'c1'" in captured.out

    month_keys = {
        (event.occurred_at.year, event.occurred_at.month) for event in published_events
    }
    reports = [reporting.get_report(year, month) for year, month in month_keys]

    assert sum(report.new_patients for report in reports) == 1
    assert sum(report.cases_opened for report in reports) == 1
    assert sum(report.meds_prescribed for report in reports) == 2


def test_prescribe_requires_existing_case() -> None:
    repo = InMemoryCaseRepository()
    prescribe = PrescribeMedication(repo, SpyBus())

    with pytest.raises(DomainError, match="not found"):
        prescribe("missing", "Amoxicillin")
