from datetime import date

import pytest

from clinicare.domain.events import PatientRegistered
from clinicare.domain.exceptions import DomainError
from clinicare.domain.patients import Patient


def test_patient_dob_must_be_in_past() -> None:
    with pytest.raises(DomainError, match="Date of birth"):
        Patient.register("p1", "Alice", date.today())


def test_patient_name_must_not_be_empty() -> None:
    with pytest.raises(DomainError, match="name"):
        Patient.register("p1", "   ", date(1990, 5, 2))


def test_register_emits_patient_registered_event() -> None:
    patient = Patient.register("p1", "Alice", date(1990, 5, 2))

    events = patient.pull_events()

    assert len(events) == 1
    assert isinstance(events[0], PatientRegistered)
    assert events[0].patient_id == "p1"


def test_pull_events_clears_the_buffer() -> None:
    patient = Patient.register("p1", "Alice", date(1990, 5, 2))

    first_pull = patient.pull_events()
    second_pull = patient.pull_events()

    assert len(first_pull) == 1
    assert second_pull == []
