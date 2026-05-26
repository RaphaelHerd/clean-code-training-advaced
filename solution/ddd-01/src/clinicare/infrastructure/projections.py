from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Tuple

from clinicare.domain.events import CaseOpened, DomainEvent, MedicationPrescribed, PatientRegistered


@dataclass
class MonthlyReport:
    new_patients: int = 0
    cases_opened: int = 0
    meds_prescribed: int = 0


class ReportingProjection:
    def __init__(self) -> None:
        # (year, month) -> MonthlyReport.
        # defaultdict auto-creates a zeroed report for any month on first access,
        # so get_report() never raises KeyError for months with no activity.
        self._reports: DefaultDict[Tuple[int, int], MonthlyReport] = defaultdict(MonthlyReport)

    def _key(self, event: DomainEvent) -> Tuple[int, int]:
        # Extract the (year, month) key from the event timestamp.
        return (event.occurred_at.year, event.occurred_at.month)

    def on_patient_registered(self, event: PatientRegistered) -> None:
        # Increment the counter for the month the event occurred.
        # We use only event.occurred_at — patient name is never stored here.
        self._reports[self._key(event)].new_patients += 1

    def on_case_opened(self, event: CaseOpened) -> None:
        self._reports[self._key(event)].cases_opened += 1

    def on_medication_prescribed(self, event: MedicationPrescribed) -> None:
        self._reports[self._key(event)].meds_prescribed += 1

    def get_report(self, year: int, month: int) -> MonthlyReport:
        # Read-only access — defaultdict returns a zeroed report for empty months.
        return self._reports[(year, month)]
