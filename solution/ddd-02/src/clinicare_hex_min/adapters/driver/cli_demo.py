from datetime import date
from clinicare_hex_min.adapters.driven.in_memory_repo import InMemoryPatientRepository
from clinicare_hex_min.adapters.driven.in_memory_event_bus import SimpleEventBus
from clinicare_hex_min.adapters.driven.system_clock import SystemClock
from clinicare_hex_min.adapters.driven.projection import MonthlyNewPatientsProjection
from clinicare_hex_min.core.application.use_cases import RegisterPatient
from clinicare_hex_min.core.domain.events import PatientRegistered

def main() -> None:
    repo = InMemoryPatientRepository()
    bus = SimpleEventBus()
    clock = SystemClock()

    projection = MonthlyNewPatientsProjection()

    # Wire the projection to the event bus.
    # From this point on, every PatientRegistered event published through `bus`
    # will automatically call projection.on_patient_registered — no manual calls needed.
    bus.subscribe(PatientRegistered, projection.on_patient_registered)

    register = RegisterPatient(repo, bus, clock)
    register("p1", "Alice", date(1990, 5, 2))
    register("p2", "Bob", date(1985, 3, 14))

    now = clock.now()
    print(f"New patients this month: {projection.count_for(now.year, now.month)}")

if __name__ == "__main__":
    main()