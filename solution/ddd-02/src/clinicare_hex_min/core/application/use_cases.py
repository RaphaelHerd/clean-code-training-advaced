from datetime import date
from clinicare_hex_min.core.domain.patients import Patient, PatientId
from clinicare_hex_min.core.domain.exceptions import DomainError
from clinicare_hex_min.core.ports.repositories import PatientRepository
from clinicare_hex_min.core.ports.events import EventPublisher
from clinicare_hex_min.core.ports.clock import Clock

class RegisterPatient:
    def __init__(self, repo: PatientRepository, events: EventPublisher, clock: Clock) -> None:
        self.repo = repo
        self.events = events
        self.clock = clock

    def __call__(self, patient_id: str, name: str, dob: date) -> Patient:
        # Step 1: idempotency guard — prevent duplicate registrations.
        # The use case enforces uniqueness; the domain does not know about the repo.
        if self.repo.get(PatientId(patient_id)):
            raise DomainError("Patient already exists")

        # Step 2: delegate construction to the domain factory method.
        # self.clock.now() is injected so tests can pass a fixed timestamp
        # instead of depending on the real system clock.
        patient = Patient.register(patient_id, name, dob, at=self.clock.now())

        # Step 3: persist the aggregate before publishing events.
        # If persistence fails the events are never emitted — no phantom events.
        self.repo.save(patient)

        # Step 4: drain the event buffer and publish each event.
        # pull_events() clears the buffer, so events are published exactly once.
        for e in patient.pull_events():
            self.events.publish(e)

        # Step 5: return the aggregate so the caller can inspect or display it.
        return patient