from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import DefaultDict, Tuple
from clinicare_hex_min.core.domain.events import PatientRegistered

@dataclass
class MonthlyCount:
    new_patients: int = 0

class MonthlyNewPatientsProjection:
    def __init__(self) -> None:
        self._data: DefaultDict[Tuple[int, int], MonthlyCount] = defaultdict(MonthlyCount)

    @staticmethod
    def _key(dt: datetime) -> Tuple[int, int]:
        return (dt.year, dt.month)

    def on_patient_registered(self, e: PatientRegistered) -> None:
        # _key extracts (year, month) from the event timestamp.
        # defaultdict auto-creates a zeroed MonthlyCount if the key is new.
        # No patient name or identifier is stored — only the count increases.
        key = self._key(e.occurred_at)
        self._data[key].new_patients += 1

    def count_for(self, year: int, month: int) -> int:
        return self._data[(year, month)].new_patients