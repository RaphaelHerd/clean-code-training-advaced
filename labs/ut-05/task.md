# 🧪 Lab UT-05 — Handwritten Mock Objects

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Interaction Testing · Mock Objects · Stub vs. Mock &nbsp;|&nbsp; 📐 Artifacts: `log_analyzer.py` · `web_service.py` · `test_log_analyzer.py`

---

## 📖 Context

Up to now your tests have checked **return values** — the classic *state-based* style. But sometimes the important question is not *what a function returns* but *whether it called something else correctly*. This is **interaction testing**.

When `LogAnalyzer` detects an invalid filename it must notify an external web service. There is nothing to return — the observable behaviour is the *outgoing call*. A stub cannot verify this: stubs can fake return values, but they cannot fail the test if an expected call never happened.

That is the job of a **mock object**. A mock records every call made to it and lets the test assert that the right calls occurred, with the right arguments, the right number of times.

> **Rule:** A stub cannot fail a test. A mock can. There should be **no more than one mock per test** — if you need more, split the test.

---

## ✅ Your Tasks

### 📁 Step 1 — Create the New Files

```python
# web_service.py

from typing import Protocol


class WebService(Protocol):
    def log_error(self, message: str) -> None:
        ...


class RealWebService:
    """Production implementation — calls an actual HTTP endpoint."""

    def log_error(self, message: str) -> None:
        # In production this would POST to an API endpoint.
        raise NotImplementedError("Not used in tests")
```

```python
# log_analyzer.py

from typing import Protocol
from extension_manager import ExtensionManager
from web_service import WebService


class LogAnalyzer:
    def __init__(self, manager: ExtensionManager, web_service: WebService):
        self._manager = manager
        self._web_service = web_service

    def analyze(self, filename: str) -> None:
        """Analyze a filename. Notify the web service if the extension is invalid."""
        if not filename:
            raise ValueError("Filename cannot be empty")
        extension = filename[filename.rfind("."):]
        if extension not in self._manager.get_managed_extension_list():
            self._web_service.log_error(f"Invalid log file detected: {filename}")
```

Copy `extension_manager.py` from UT-03 unchanged.

---

### 🔍 Step 2 — Understand Why a Stub Is Not Enough

You could try to test the notification with a stub:

```python
class StubWebService:
    def log_error(self, message: str) -> None:
        pass  # does nothing
```

Write this test and run it:

```python
def test_analyze_invalid_file_notifies_web_service_stub_attempt():
    stub_manager = StubExtensionManager()
    stub_service = StubWebService()
    analyzer = LogAnalyzer(manager=stub_manager, web_service=stub_service)

    analyzer.analyze("report.xml")

    # How do you assert the call happened? You cannot — stub gives you nothing.
    assert True  # this always passes, proving nothing
```

The test passes even if you delete the entire notification line from `analyze`. The stub hides the bug.

---

### 🧱 Step 3 — Write a Handwritten Mock

A mock records every call so the test can interrogate it afterwards:

```python
class MockWebService:
    def __init__(self):
        self.log_error_was_called = False
        self.last_error_message: str | None = None
        self.call_count = 0

    def log_error(self, message: str) -> None:
        self.log_error_was_called = True
        self.last_error_message = message
        self.call_count += 1
```

---

### 🧪 Step 4 — Write Interaction Tests Using the Mock

```python
# test_log_analyzer.py

import pytest
from log_analyzer import LogAnalyzer

class StubExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        return [".log"]


class MockWebService:
    def __init__(self):
        self.log_error_was_called = False
        self.last_error_message: str | None = None
        self.call_count = 0

    def log_error(self, message: str) -> None:
        self.log_error_was_called = True
        self.last_error_message = message
        self.call_count += 1


@pytest.fixture
def mock_service():
    return MockWebService()


@pytest.fixture
def analyzer(mock_service: MockWebService):
    return LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=mock_service,
    )


def test_analyze_invalid_extension_calls_log_error(analyzer: LogAnalyzer, mock_service: MockWebService):
    # Act
    analyzer.analyze("report.xml")

    # Assert interaction
    assert mock_service.log_error_was_called is True


def test_analyze_invalid_extension_sends_filename_in_message(analyzer: LogAnalyzer, mock_service: MockWebService):
    analyzer.analyze("report.xml")

    if mock_service.last_error_message is None:
        pytest.fail("Expected log_error to be called with a message, but it was not called.")
    
    assert "report.xml" in mock_service.last_error_message


def test_analyze_valid_extension_does_not_call_log_error(analyzer: LogAnalyzer, mock_service: MockWebService):
    analyzer.analyze("system.log")

    assert mock_service.log_error_was_called is False


def test_analyze_invalid_extension_calls_log_error_exactly_once(analyzer: LogAnalyzer, mock_service: MockWebService):
    analyzer.analyze("report.xml")

    assert mock_service.call_count == 1
```

---

### 🤔 Step 5 — Stub vs. Mock: Know the Difference

Fill in this comparison table as a comment block in `test_log_analyzer.py`:

```python
# STUB vs. MOCK COMPARISON
# ┌─────────────────────────────┬──────────────────────┬──────────────────────┐
# │ Property                    │ Stub                 │ Mock                 │
# ├─────────────────────────────┼──────────────────────┼──────────────────────┤
# │ Purpose                     │                      │                      │
# │ Can fail a test?            │                      │                      │
# │ Checks return values?       │                      │                      │
# │ Checks outgoing calls?      │                      │                      │
# │ Recommended per test        │                      │                      │
# └─────────────────────────────┴──────────────────────┴──────────────────────┘
```

---

### ▶️ Step 6 — Run Your Tests

```bash
pytest -v
```

All tests must pass. Delete the `self._web_service.log_error(...)` line from `analyze` temporarily and confirm that `test_analyze_invalid_extension_calls_log_error` turns red — proving the mock actually guards the behaviour.

Restore the line before submitting.

---

## 📦 Deliverable

1. `web_service.py` — `WebService` protocol + `RealWebService` stub (not used in tests)
2. `log_analyzer.py` — `LogAnalyzer` with `analyze` method that calls the web service on invalid files
3. `extension_manager.py` — unchanged from UT-03
4. `test_log_analyzer.py` — `MockWebService` + at least **5 interaction tests** + stub-vs-mock comparison table
5. All tests passing with `pytest -v`

---

> 🏗️ *You now know the fundamental difference between stubs and mocks. In UT-06 both appear in the same test — the web service fails and an email must be sent. That scenario requires exactly one mock and one stub working together.*
