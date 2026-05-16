import pytest

from clinicare.domain.cases import Case, MedicationOrder
from clinicare.domain.events import CaseOpened, MedicationPrescribed
from clinicare.domain.exceptions import DomainError

def test_cannot_prescribe_to_closed_case() -> None:
    case = Case.open("c1", "p1")
    case.close()

    with pytest.raises(DomainError, match="Cannot prescribe"):
        case.prescribe("Amoxicillin")


def test_cannot_close_case_twice() -> None:
    case = Case.open("c1", "p1")
    case.close()

    with pytest.raises(DomainError, match="already closed"):
        case.close()

def test_open_case_emits_case_opened_event() -> None:
    case = Case.open("c1", "p1")

    events = case.pull_events()

    assert len(events) == 1
    assert isinstance(events[0], CaseOpened)
    assert events[0].case_id == "c1"
    assert events[0].patient_id == "p1"


def test_prescribe_adds_medication_order_and_event() -> None:
    case = Case.open("c1", "p1")
    case.pull_events()

    case.prescribe("Amoxicillin")
    events = case.pull_events()

    assert case.medications == [MedicationOrder("Amoxicillin")]
    assert len(events) == 1
    assert isinstance(events[0], MedicationPrescribed)
    assert events[0].medication == "Amoxicillin"
