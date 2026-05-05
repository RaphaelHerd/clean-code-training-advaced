# 🧪 Lab DDD-01 — Modelling ClinicCare with Domain-Driven Design

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: DDD · Bounded Contexts · Aggregates · Value Objects · Domain Events &nbsp;|&nbsp; 📐 Artifacts: `clinicare/` package · `CONTEXT_MAP.md` · `tests/`

---

## 📖 Context

Domain-Driven Design is a way of structuring software so that the code reflects the business problem it solves — not the technical tools used to build it. The domain model lives at the centre; frameworks, databases, and APIs are details at the edge.

In this lab you build **ClinicCare**, a minimal patient management system for a small outpatient clinic. The system must register patients, open treatment cases, prescribe medications, and emit domain events that feed a reporting projection.

You will go through the full DDD cycle: draw the bounded contexts first, model the aggregates and value objects, enforce domain invariants, wire an event bus, and build a reporting read model — all in plain Python, runnable from the command line.

---

## ✅ Your Tasks

### 🗣️ Ubiquitous Language

Before writing a single line of code, agree on the vocabulary. Every class, method, and variable name in this lab must use these terms:

| Term | Meaning |
|---|---|
| **Patient** | A registered person receiving care |
| **Case** | A treatment episode — can be open or closed |
| **MedicationOrder** | A prescribed medication, part of a Case |
| **Alert** | Raised when a domain rule is violated (e.g. conflicting medications) |
| **Report** | Monthly summary for clinic administration |

---

### 📁 Step 1 — Create the Project Structure

Create the following folder structure. Each `__init__.py` may be empty.

```
clinicare/
├── domain/
│   ├── __init__.py
│   ├── patients.py
│   ├── cases.py
│   ├── events.py
│   └── exceptions.py
├── application/
│   ├── __init__.py
│   └── use_cases.py
├── infrastructure/
│   ├── __init__.py
│   ├── repositories.py
│   ├── event_bus.py
│   └── projections.py
└── cli/
    └── demo.py
tests/
├── test_domain_patients.py
└── test_use_cases.py
```

> 💡 **Tip:** Domain must never import from `application` or `infrastructure`. Application may import from `domain`. Infrastructure may import from both. Draw the allowed arrows on paper before coding.

---

### 🗺️ Step 2 — Draw the Bounded Contexts

Before writing any code, draw a context map on paper or whiteboard. Keep it to three contexts:

- **Patient Management** — register and update patient information
- **Treatment** — open/close cases and prescribe medication
- **Reporting** — count monthly admissions and prescriptions

For each context, note: what data does it own, what events does it produce, what events does it consume?

### 🧬 Step 3 — Model the Core Domain

Implement the main entities and value objects in `clinicare/domain/`.

#### `exceptions.py`

```python
class DomainError(Exception):
    pass
```

#### `events.py`

Define a base `DomainEvent` frozen dataclass and three concrete events:

```python
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass(frozen=True)
class DomainEvent:
    id: str
    occurred_at: datetime

# Each concrete event carries only the identifiers that downstream consumers
# need to do their job.  Sensitive fields (patient names, medication dosages)
# are intentionally excluded — events cross context boundaries and must not
# leak private data.

@dataclass(frozen=True)
class PatientRegistered(DomainEvent):
    patient_id: str         # enough for the reporting projection to count registrations

@dataclass(frozen=True)
class CaseOpened(DomainEvent):
    case_id: str
    patient_id: str         # links the case back to the patient context

@dataclass(frozen=True)
class MedicationPrescribed(DomainEvent):
    case_id: str
    medication: str         # medication name — not a dosage or patient identifier

def new_event_id() -> str:
    return str(uuid.uuid4())
```

#### `patients.py`

`Patient` is an aggregate root. Enforce these invariants in `__post_init__`:

- Date of birth must be in the past
- Name must not be empty

Add a `register` class method that constructs the aggregate and appends a `PatientRegistered` event to an internal `_events` buffer. Add a `pull_events` method that drains and returns the buffer.

```python
# clinicare/domain/patients.py

from dataclasses import dataclass, field
from datetime import date, datetime
from .events import PatientRegistered, new_event_id
from .exceptions import DomainError


@dataclass(frozen=True)
class PatientId:
    # Value object: identity is the string value, not the object reference.
    value: str


@dataclass
class Patient:
    patient_id: PatientId
    name: str
    date_of_birth: date
    # Transient event buffer — not part of the public interface.
    # Field is excluded from __init__ and __repr__ to keep it invisible.
    _events: list = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        # Invariant: a patient cannot be born in the future.
        if self.date_of_birth >= date.today():
            raise DomainError("Date of birth must be in the past")
        # Invariant: every patient must have a non-empty name.
        if not self.name or not self.name.strip():
            raise DomainError("Patient name must not be empty")

    @classmethod
    def register(cls, patient_id: str, name: str, dob: date) -> "Patient":
        # Factory method keeps construction and first-event emission together.
        # Callers never call the constructor directly — they always use register().
        p = cls(patient_id=PatientId(patient_id), name=name, date_of_birth=dob)
        # Buffer the event — do NOT publish here.  The application layer drains
        # the buffer only after the aggregate has been persisted successfully,
        # preventing ghost events if persistence fails.
        p._events.append(
            PatientRegistered(
                id=new_event_id(),
                occurred_at=datetime.utcnow(),
                patient_id=patient_id,
            )
        )
        return p

    def pull_events(self) -> list:
        # Atomic swap: copy the buffer, reset it, return the copy.
        # This guarantees no event is published twice even under concurrent calls.
        ev, self._events = self._events, []
        return ev
```

#### `cases.py`

`Case` is a second aggregate root. Enforce these invariants:

- A `MedicationOrder` can only be added when the case is open
- A case cannot be closed twice

Use a `MedicationOrder` **value object** (frozen dataclass) to represent a prescribed medication — it should be immutable and carry no identity of its own.

```python
# clinicare/domain/cases.py

from dataclasses import dataclass, field
from datetime import datetime
from .events import CaseOpened, MedicationPrescribed, new_event_id
from .exceptions import DomainError


@dataclass(frozen=True)
class MedicationOrder:
    # Value object: immutable, no identity.  Two orders for the same medication
    # are equal by value — identical to comparing two integers.
    medication: str


@dataclass
class Case:
    case_id: str
    patient_id: str
    _is_open: bool = field(default=True, init=False)
    _medications: list = field(default_factory=list, init=False, repr=False)
    _events: list = field(default_factory=list, init=False, repr=False)

    @classmethod
    def open(cls, case_id: str, patient_id: str) -> "Case":
        # Factory method: every new Case starts in the open state.
        c = cls(case_id=case_id, patient_id=patient_id)
        c._events.append(
            CaseOpened(
                id=new_event_id(),
                occurred_at=datetime.utcnow(),
                case_id=case_id,
                patient_id=patient_id,
            )
        )
        return c

    def prescribe(self, medication: str) -> None:
        # Invariant: prescriptions require an open case.
        # Business rule lives here in the domain, not in the application layer.
        if not self._is_open:
            raise DomainError(f"Cannot prescribe to closed case '{self.case_id}'")
        self._medications.append(MedicationOrder(medication=medication))
        self._events.append(
            MedicationPrescribed(
                id=new_event_id(),
                occurred_at=datetime.utcnow(),
                case_id=self.case_id,
                medication=medication,
            )
        )

    def close(self) -> None:
        # Invariant: closing an already-closed case is an error.
        if not self._is_open:
            raise DomainError(f"Case '{self.case_id}' is already closed")
        self._is_open = False

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def medications(self) -> list:
        return list(self._medications)  # defensive copy — callers cannot mutate internals

    def pull_events(self) -> list:
        ev, self._events = self._events, []
        return ev
```

---

### 🧪 Step 4 — Prove Domain Rules with Tests

Write `tests/test_domain_patients.py`. At minimum, test:

```python
def test_patient_dob_must_be_in_past():
    ...

def test_register_emits_patient_registered_event():
    ...

def test_pull_events_clears_the_buffer():
    ...
```

And `tests/test_domain_cases.py`:

```python
def test_cannot_prescribe_to_closed_case():
    ...

def test_cannot_close_case_twice():
    ...
```

Run `pytest -v`. All must pass before moving on.

---

### 📢 Step 5 — Build the Event Bus

Implement `clinicare/infrastructure/event_bus.py`:

```python
# clinicare/infrastructure/event_bus.py


class EventBus:
    def __init__(self):
        # Maps event class → list of handler callables.
        # A dict of lists is the simplest pub/sub structure possible.
        self._handlers: dict = {}

    def subscribe(self, event_type, handler) -> None:
        # Register a handler callable for a specific event type.
        # setdefault initialises the list on the first subscription for that type.
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event) -> None:
        # Deliver the event to every handler whose subscribed type matches.
        # isinstance allows a handler subscribed to DomainEvent to receive all
        # concrete event subtypes — useful for catch-all logging handlers.
        for event_type, handlers in self._handlers.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    handler(event)
```

Wire a handler that raises an `Alert` (print a warning is sufficient) when the same medication is prescribed twice within the same case.

```python
# Example alert handler — register with:
# bus.subscribe(MedicationPrescribed, duplicate_medication_alert(seen))

def duplicate_medication_alert(seen: set):
    """Returns a handler that warns when the same medication appears twice."""
    def handler(event):
        key = (event.case_id, event.medication)
        if key in seen:
            print(f"ALERT: '{event.medication}' prescribed twice in case '{event.case_id}'")
        seen.add(key)
    return handler
```

---

### 🧰 Step 6 — Implement the Application Layer

Add use cases in `clinicare/application/use_cases.py`. Each use case must:

1. Validate preconditions via the repository
2. Call the domain method
3. Persist the aggregate
4. Publish events from `pull_events()` through the event bus

Implement these four use cases:

```python
# clinicare/application/use_cases.py

from clinicare.domain.patients import Patient, PatientId
from clinicare.domain.cases import Case
from clinicare.domain.exceptions import DomainError


class RegisterPatient:
    def __init__(self, patient_repo, bus):
        self._patient_repo = patient_repo
        self._bus = bus

    def __call__(self, patient_id: str, name: str, dob):
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
    def __init__(self, patient_repo, case_repo, bus):
        self._patient_repo = patient_repo
        self._case_repo = case_repo
        self._bus = bus

    def __call__(self, case_id: str, patient_id: str):
        # Cross-aggregate check: the patient must exist before a case can be opened.
        if not self._patient_repo.get(patient_id):
            raise DomainError(f"Patient '{patient_id}' not found")
        case = Case.open(case_id, patient_id)
        self._case_repo.save(case)
        for event in case.pull_events():
            self._bus.publish(event)
        return case


class PrescribeMedication:
    def __init__(self, case_repo, bus):
        self._case_repo = case_repo
        self._bus = bus

    def __call__(self, case_id: str, medication: str):
        case = self._case_repo.get(case_id)
        if not case:
            raise DomainError(f"Case '{case_id}' not found")
        # Domain enforces the invariant (case must be open) — not this use case.
        case.prescribe(medication)
        self._case_repo.save(case)
        for event in case.pull_events():
            self._bus.publish(event)


class CloseCase:
    def __init__(self, case_repo, bus):
        self._case_repo = case_repo
        self._bus = bus

    def __call__(self, case_id: str):
        case = self._case_repo.get(case_id)
        if not case:
            raise DomainError(f"Case '{case_id}' not found")
        # Domain enforces the invariant (cannot close twice) — not this use case.
        case.close()
        self._case_repo.save(case)
        for event in case.pull_events():
            self._bus.publish(event)
```

---

### 📊 Step 7 — Build the Reporting Projection

Implement `clinicare/infrastructure/projections.py`. Subscribe to domain events and maintain monthly counters:

```python
# clinicare/infrastructure/projections.py

from dataclasses import dataclass
from collections import defaultdict


@dataclass
class MonthlyReport:
    # Only integer counters — no names, no identifiers, no PII.
    new_patients: int = 0
    cases_opened: int = 0
    meds_prescribed: int = 0


class ReportingProjection:
    def __init__(self):
        # (year, month) → MonthlyReport.
        # defaultdict auto-creates a zeroed report for any month on first access,
        # so get_report() never raises KeyError for months with no activity.
        self._reports: dict = defaultdict(MonthlyReport)

    def _key(self, event) -> tuple:
        # Extract the (year, month) key from the event timestamp.
        return (event.occurred_at.year, event.occurred_at.month)

    def on_patient_registered(self, event) -> None:
        # Increment the counter for the month the event occurred.
        # We use only event.occurred_at — patient name is never stored here.
        self._reports[self._key(event)].new_patients += 1

    def on_case_opened(self, event) -> None:
        self._reports[self._key(event)].cases_opened += 1

    def on_medication_prescribed(self, event) -> None:
        self._reports[self._key(event)].meds_prescribed += 1

    def get_report(self, year: int, month: int) -> MonthlyReport:
        # Read-only access — defaultdict returns a zeroed report for empty months.
        return self._reports[(year, month)]
```

> 💡 **Privacy rule:** The report must never contain patient names or any personally identifiable information — only counts and totals. Write a test that asserts this.

---

### 🚀 Step 8 — Wire the CLI Demo

Implement `clinicare/cli/demo.py` that runs a realistic scenario end to end:

1. Register two patients
2. Open a case for each
3. Prescribe two medications to the first case
4. Close the first case
5. Print the monthly report

```bash
python -m clinicare.cli.demo
```

Expected output (values will vary):

```
Registered patient p1: Alice
Registered patient p2: Bob
Opened case c1 for p1
Prescribed Amoxicillin to c1
Prescribed Ibuprofen to c1
Closed case c1
--- Monthly Report (2025-05) ---
New patients : 2
Cases opened : 2
Meds prescribed: 2
```

---

## 📦 Deliverable

1. `clinicare/domain/` — `Patient`, `Case`, `MedicationOrder` value object, `DomainEvent` hierarchy, `DomainError`
2. `clinicare/infrastructure/` — `EventBus`, in-memory repositories, `ReportingProjection`
3. `clinicare/application/` — four use cases
4. `clinicare/cli/demo.py` — runnable end-to-end scenario
5. `tests/` — at least **8 tests** covering domain invariants, event emission, use case orchestration, and privacy of reports

---

> 🏗️ *In DDD-02 you will revisit the same domain through a different architectural lens — Hexagonal Architecture — and implement just one focused slice of it with clearly defined ports and adapters.*
