from datetime import date, datetime

from clinicare.application.use_cases import (
    CloseCase,
    OpenCase,
    PrescribeMedication,
    RegisterPatient,
)
from clinicare.domain.events import CaseOpened, MedicationPrescribed, PatientRegistered
from clinicare.infrastructure.event_bus import EventBus, duplicate_medication_alert
from clinicare.infrastructure.projections import ReportingProjection
from clinicare.infrastructure.repositories import (
    InMemoryCaseRepository,
    InMemoryPatientRepository,
)


def main() -> None:
    patient_repo = InMemoryPatientRepository()
    case_repo = InMemoryCaseRepository()
    bus = EventBus()
    reporting = ReportingProjection()

    bus.subscribe(PatientRegistered, reporting.on_patient_registered)
    bus.subscribe(CaseOpened, reporting.on_case_opened)
    bus.subscribe(MedicationPrescribed, reporting.on_medication_prescribed)
    bus.subscribe(MedicationPrescribed, duplicate_medication_alert(set()))

    register_patient = RegisterPatient(patient_repo, bus)
    open_case = OpenCase(patient_repo, case_repo, bus)
    prescribe_medication = PrescribeMedication(case_repo, bus)
    close_case = CloseCase(case_repo, bus)

    register_patient("p1", "Alice", date(1990, 5, 2))
    print("Registered patient p1: Alice")
    register_patient("p2", "Bob", date(1985, 3, 14))
    print("Registered patient p2: Bob")

    open_case("c1", "p1")
    print("Opened case c1 for p1")
    open_case("c2", "p2")
    print("Opened case c2 for p2")

    prescribe_medication("c1", "Amoxicillin")
    print("Prescribed Amoxicillin to c1")
    prescribe_medication("c1", "Ibuprofen")
    print("Prescribed Ibuprofen to c1")

    close_case("c1")
    print("Closed case c1")

    now = datetime.utcnow()
    report = reporting.get_report(now.year, now.month)
    print(f"--- Monthly Report ({now.year:04d}-{now.month:02d}) ---")
    print(f"New patients : {report.new_patients}")
    print(f"Cases opened : {report.cases_opened}")
    print(f"Meds prescribed: {report.meds_prescribed}")


if __name__ == "__main__":
    main()
