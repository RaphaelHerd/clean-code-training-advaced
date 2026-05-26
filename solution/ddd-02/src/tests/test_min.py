from datetime import date

from clinicare_hex_min.adapters.driven.in_memory_event_bus import SimpleEventBus
from clinicare_hex_min.adapters.driven.system_clock import SystemClock
from clinicare_hex_min.adapters.driven.in_memory_repo import InMemoryPatientRepository
from clinicare_hex_min.adapters.driven.projection import (
    MonthlyNewPatientsProjection,
)
from clinicare_hex_min.core.application.use_cases import RegisterPatient
from clinicare_hex_min.core.domain.events import PatientRegistered


def test_register_patient_increments_monthly_projection() -> None:
    repo = InMemoryPatientRepository()
    bus = SimpleEventBus()
    clock = SystemClock()
    proj = MonthlyNewPatientsProjection()
    bus.subscribe(PatientRegistered, proj.on_patient_registered)

    register = RegisterPatient(repo, bus, clock)
    register("p1", "Alice", date(1990, 5, 2))

    now = clock.now()
    assert proj.count_for(now.year, now.month) == 1


def test_registering_duplicate_patient_raises_domain_error() -> None:
    from clinicare_hex_min.core.domain.exceptions import DomainError
    import pytest

    repo = InMemoryPatientRepository()
    bus = SimpleEventBus()
    clock = SystemClock()

    register = RegisterPatient(repo, bus, clock)
    register("p1", "Alice", date(1990, 5, 2))

    with pytest.raises(DomainError):
        register("p1", "Alice", date(1990, 5, 2))
