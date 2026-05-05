# 🧪 Lab DDD-02 — Hexagonal Architecture: One Slice of ClinicCare

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Hexagonal Architecture · Ports & Adapters · Domain Events · Projections &nbsp;|&nbsp; 📐 Artifacts: `clinicare_hex_min/` package · `tests/test_min.py`

---

## 📖 Context

Hexagonal Architecture (also called Ports & Adapters) separates the business core from the outside world by defining strict boundaries: **ports** are interfaces the core exposes or requires, **adapters** are the concrete implementations that plug into those ports from the outside.

The result is a core that has zero knowledge of databases, HTTP, or any framework — and can be tested in complete isolation.

## 📦 Setup

No external dependencies are required — only the Python standard library and pytest.

```bash
pip install pytest
```

---

## 📁 Project Structure

Create the following files exactly as shown. The skeleton code is provided for each file in the steps below.

```
clinicare_hex_min/
├── core/
│   ├── domain/
│   │   ├── patients.py
│   │   ├── events.py
│   │   └── exceptions.py
│   ├── application/
│   │   └── use_cases.py
│   └── ports/
│       ├── repositories.py
│       ├── events.py
│       └── clock.py
├── adapters/
│   ├── driven/
│   │   ├── in_memory_repo.py
│   │   ├── in_memory_event_bus.py
│   │   ├── system_clock.py
│   │   └── projection.py
│   └── driver/
│       └── cli_demo.py
└── tests/
    └── test_min.py
```

> 💡 **Architecture rule:** `core/` must never import from `adapters/`. The dependency arrow always points inward — adapters depend on the core, never the other way around.

---

## ✅ Your Tasks

### 📁 Step 1 — Create the Domain Layer

Copy these files exactly. They are complete and require no changes.

#### `core/domain/exceptions.py`

```python
class DomainError(Exception):
    pass
```

#### `core/domain/events.py`

```python
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass(frozen=True)
class DomainEvent:
    id: str
    occurred_at: datetime

@dataclass(frozen=True)
class PatientRegistered(DomainEvent):
    patient_id: str

def new_event_id() -> str:
    return str(uuid.uuid4())
```

#### `core/ports/repositories.py`

```python
from typing import Protocol, Optional
from clinicare_hex_min.core.domain.patients import Patient, PatientId

class PatientRepository(Protocol):
    def get(self, pid: PatientId) -> Optional[Patient]: ...
    def save(self, patient: Patient) -> None: ...
```

#### `core/ports/events.py`

```python
from typing import Protocol
from clinicare_hex_min.core.domain.events import DomainEvent

class EventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
```

#### `core/ports/clock.py`

```python
from typing import Protocol
from datetime import datetime

class Clock(Protocol):
    def now(self) -> datetime: ...
```

#### `adapters/driven/system_clock.py`

```python
from datetime import datetime, timezone
from clinicare_hex_min.core.ports.clock import Clock

class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
```

---

### 🔧 Step 2 — Implement `Patient.register` (TODO)

Copy this skeleton into `core/domain/patients.py` and fill in the `TODO`:

```python
from dataclasses import dataclass, field
from datetime import date, datetime
from .exceptions import DomainError
from .events import PatientRegistered, new_event_id

@dataclass(frozen=True)
class PatientId:
    value: str

@dataclass
class Patient:
    patient_id: PatientId
    name: str
    date_of_birth: date
    _events: list = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        if self.date_of_birth >= date.today():
            raise DomainError("Date of birth must be in the past")

    @classmethod
    def register(cls, pid: str, name: str, dob: date, at: datetime) -> "Patient":
        # Step 1: construct the aggregate.
        # cls(...) triggers __post_init__, which enforces the date-of-birth invariant.
        # If the invariant fails, DomainError is raised before any event is buffered.
        p = cls(patient_id=PatientId(pid), name=name, date_of_birth=dob)

        # Step 2: record what happened as an immutable domain event.
        # We pass `at` from outside so the use case (or a test) controls the clock —
        # the domain never calls datetime.now() directly, keeping it deterministic.
        p._events.append(
            PatientRegistered(
                id=new_event_id(),
                occurred_at=at,
                patient_id=pid,
            )
        )

        # Step 3: return the aggregate to the caller (the use case).
        # The caller is responsible for persisting it and publishing the events.
        return p

    def pull_events(self) -> list:
        ev, self._events = self._events, []
        return ev
```

---

### 🔧 Step 3 — Implement the In-Memory Repository (TODO)

Copy this skeleton into `adapters/driven/in_memory_repo.py` and fill in the two TODOs:

```python
from typing import Dict, Optional
from clinicare_hex_min.core.domain.patients import Patient, PatientId

class InMemoryPatientRepository:
    def __init__(self):
        self._store: Dict[str, Patient] = {}

    def get(self, pid: PatientId) -> Optional[Patient]:
        # pid.value is the plain string identifier (e.g. "p1").
        # dict.get() returns None automatically when the key is absent,
        # so callers can check `if repo.get(pid)` without catching exceptions.
        return self._store.get(pid.value)

    def save(self, patient: Patient) -> None:
        # Overwrite any existing entry — this acts as both insert and update.
        # In a real repository this would call an ORM or execute a SQL UPSERT.
        self._store[patient.patient_id.value] = patient
```

---

### 🔧 Step 4 — Implement the Event Bus (TODO)

Copy this skeleton into `adapters/driven/in_memory_event_bus.py` and fill in the two TODOs:

```python
from typing import Callable, Dict, List, Type
from clinicare_hex_min.core.domain.events import DomainEvent

class SimpleEventBus:
    def __init__(self):
        self._subs: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        # setdefault creates an empty list the first time a type is registered,
        # then appends the handler.  Multiple handlers per type are fully supported.
        self._subs.setdefault(event_type, []).append(handler)

    def publish(self, event: DomainEvent) -> None:
        # isinstance allows subclass events to match parent-type subscriptions.
        # For example, a handler subscribed to DomainEvent would receive every event.
        for event_type, handlers in self._subs.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    # Call the handler synchronously.  In production you might
                    # push to a queue instead, but in-memory is correct here.
                    handler(event)
```

---

### 🔧 Step 5 — Implement the Projection (TODO)

Copy this skeleton into `adapters/driven/projection.py` and fill in the TODO:

```python
from collections import defaultdict
from dataclasses import dataclass
from clinicare_hex_min.core.domain.events import PatientRegistered

@dataclass
class MonthlyCount:
    new_patients: int = 0

class MonthlyNewPatientsProjection:
    def __init__(self):
        self._data = defaultdict(MonthlyCount)

    @staticmethod
    def _key(dt):
        return (dt.year, dt.month)

    def on_patient_registered(self, e: PatientRegistered) -> None:
        # _key extracts (year, month) from the event timestamp.
        # defaultdict auto-creates a zeroed MonthlyCount if the key is new.
        # No patient name or identifier is stored — only the count increases.
        key = self._key(e.occurred_at)
        self._data[key].new_patients += 1

    def count_for(self, year: int, month: int) -> int:
        return self._data[(year, month)].new_patients
```

---

### 🔧 Step 6 — Implement the `RegisterPatient` Use Case (TODO)

Copy this skeleton into `core/application/use_cases.py` and fill in the TODO:

```python
from datetime import date
from clinicare_hex_min.core.domain.patients import Patient, PatientId
from clinicare_hex_min.core.domain.exceptions import DomainError
from clinicare_hex_min.core.ports.repositories import PatientRepository
from clinicare_hex_min.core.ports.events import EventPublisher
from clinicare_hex_min.core.ports.clock import Clock

class RegisterPatient:
    def __init__(self, repo: PatientRepository, events: EventPublisher, clock: Clock):
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
```

---

### 🚀 Step 7 — Wire the CLI Demo

Copy this complete file into `adapters/driver/cli_demo.py`. It contains one final TODO:

```python
from datetime import date
from clinicare_hex_min.adapters.driven.in_memory_repo import InMemoryPatientRepository
from clinicare_hex_min.adapters.driven.in_memory_event_bus import SimpleEventBus
from clinicare_hex_min.adapters.driven.system_clock import SystemClock
from clinicare_hex_min.adapters.driven.projection import MonthlyNewPatientsProjection
from clinicare_hex_min.core.application.use_cases import RegisterPatient
from clinicare_hex_min.core.domain.events import PatientRegistered

def main():
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
```

Run the demo:

```bash
python -m clinicare_hex_min.adapters.driver.cli_demo
```

Expected output:

```
New patients this month: 2
```

---

### 🧪 Step 8 — Run the Test

Copy this file into `tests/test_min.py`. It is already written — it must pass once all TODOs are complete:

```python
from datetime import date
from clinicare_hex_min.adapters.driven.in_memory_repo import InMemoryPatientRepository
from clinicare_hex_min.adapters.driven.in_memory_event_bus import SimpleEventBus
from clinicare_hex_min.adapters.driven.system_clock import SystemClock
from clinicare_hex_min.adapters.driven.projection import MonthlyNewPatientsProjection
from clinicare_hex_min.core.application.use_cases import RegisterPatient
from clinicare_hex_min.core.domain.events import PatientRegistered

def test_register_patient_increments_monthly_projection():
    repo = InMemoryPatientRepository()
    bus = SimpleEventBus()
    clock = SystemClock()
    proj = MonthlyNewPatientsProjection()
    bus.subscribe(PatientRegistered, proj.on_patient_registered)

    register = RegisterPatient(repo, bus, clock)
    register("p1", "Alice", date(1990, 5, 2))

    now = clock.now()
    assert proj.count_for(now.year, now.month) == 1


def test_registering_duplicate_patient_raises_domain_error():
    from clinicare_hex_min.core.domain.exceptions import DomainError
    import pytest

    repo = InMemoryPatientRepository()
    bus = SimpleEventBus()
    clock = SystemClock()

    register = RegisterPatient(repo, bus, clock)
    register("p1", "Alice", date(1990, 5, 2))

    with pytest.raises(DomainError):
        register("p1", "Alice", date(1990, 5, 2))
```

```bash
pytest -v
```

Both tests must pass.

---

## ✅ Acceptance Criteria

| Rule | Check |
|---|---|
| `core/` contains no imports from `adapters/` | Grep for `adapters` in `core/` — must be empty |
| `RegisterPatient` prevents duplicate registration | `test_registering_duplicate_patient_raises_domain_error` passes |
| Projection counts new patients per (year, month) only | `test_register_patient_increments_monthly_projection` passes |
| Projection contains no patient names (no PII) | `MonthlyCount` has only integer fields |
| CLI prints a non-zero count | `python -m ... cli_demo` prints `New patients this month: 2` |

---

## 📦 Deliverable

1. All files from the project structure above, with every `TODO` implemented
2. `tests/test_min.py` — both tests passing with `pytest -v`
3. CLI demo printing the correct count

---

> 🏗️ *Hexagonal Architecture is not about the number of layers — it is about the direction of dependencies. The one rule you enforced here (core never imports adapters) is the same rule that makes large systems testable, replaceable, and long-lived.*
