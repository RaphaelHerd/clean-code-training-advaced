# 🧪 Lab UT-06 — Stub and Mock Together

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Interaction Testing · One Mock Per Test · Stub + Mock Collaboration &nbsp;|&nbsp; 📐 Artifacts: `log_analyzer.py` · `web_service.py` · `email_service.py` · `test_log_analyzer.py`

---

## 📖 Context

In UT-05 the web service was always available. In a real system it can fail — and when it does, the system must respond: send an alert email to the administrator. 

This scenario requires two fake objects in the same test:

- A **stub** for the web service — it simulates the failure by raising an exception. It is not the thing being asserted.
- A **mock** for the email service — it records whether the email was actually sent. It is the thing being asserted.

> **Rule: one mock per test.** If you have two objects both asserting interactions, you are testing two behaviours at once — split the test. All other fakes in the same test are stubs.

---

## ✅ Your Tasks

### 📁 Step 1 — Create the Email Service

```python
# email_service.py

from typing import Protocol


class EmailService(Protocol):
    def send_email(self, to: str, subject: str, body: str) -> None:
        ...


class SmtpEmailService:
    """Production implementation — sends a real email via SMTP."""

    def send_email(self, to: str, subject: str, body: str) -> None:
        raise NotImplementedError("Not used in tests")
```

---

### 📁 Step 2 — Update `LogAnalyzer`

`LogAnalyzer` now has three dependencies: extension manager, web service, and email service. When the web service raises an exception, the email service is notified.

```python
# log_analyzer.py

from extension_manager import ExtensionManager
from web_service import WebService
from email_service import EmailService

ADMIN_EMAIL = "admin@shoplog.internal"


class LogAnalyzer:
    def __init__(
        self,
        manager: ExtensionManager,
        web_service: WebService,
        email_service: EmailService,
    ):
        self._manager = manager
        self._web_service = web_service
        self._email_service = email_service

    def analyze(self, filename: str) -> None:
        if not filename:
            raise ValueError("Filename cannot be empty")
        extension = filename[filename.rfind("."):]
        if extension not in self._manager.get_managed_extension_list():
            try:
                self._web_service.log_error(f"Invalid log file: {filename}")
            except Exception as e:
                self._email_service.send_email(
                    to=ADMIN_EMAIL,
                    subject="Web service unreachable",
                    body=str(e),
                )
```

Copy `extension_manager.py`, `web_service.py` from UT-05 unchanged.

---

### 🧱 Step 3 — Write the Stub and the Mock

```python
# test_log_analyzer.py


class StubExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        return [".log"]


class StubWebServiceThatFails:
    """Simulates a web service outage — always raises."""

    def log_error(self, message: str) -> None:
        raise ConnectionError("Web service is unreachable")


class MockEmailService:
    """Records whether send_email was called and with which arguments."""

    def __init__(self):
        self.was_called = False
        self.last_to: str | None = None
        self.last_subject: str | None = None
        self.last_body: str | None = None

    def send_email(self, to: str, subject: str, body: str) -> None:
        self.was_called = True
        self.last_to = to
        self.last_subject = subject
        self.last_body = body
```

---

### 🧪 Step 4 — Write Tests That Use Both Fakes

```python
import pytest
from log_analyzer import LogAnalyzer, ADMIN_EMAIL


@pytest.fixture
def mock_email():
    return MockEmailService()


@pytest.fixture
def analyzer_with_failing_service(mock_email):
    return LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=StubWebServiceThatFails(),  # stub
        email_service=mock_email,               # mock
    )


def test_analyze_sends_email_when_web_service_fails(
    analyzer_with_failing_service, mock_email
):
    analyzer_with_failing_service.analyze("report.xml")

    assert mock_email.was_called is True


def test_analyze_email_is_sent_to_admin(
    analyzer_with_failing_service, mock_email
):
    analyzer_with_failing_service.analyze("report.xml")

    assert mock_email.last_to == ADMIN_EMAIL


def test_analyze_email_body_contains_error_reason(
    analyzer_with_failing_service, mock_email
):
    analyzer_with_failing_service.analyze("report.xml")

    assert "unreachable" in mock_email.last_body.lower()


def test_analyze_does_not_send_email_when_web_service_succeeds(mock_email):
    class StubWebServiceThatSucceeds:
        def log_error(self, message: str) -> None:
            pass  # succeeds silently

    analyzer = LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=StubWebServiceThatSucceeds(),
        email_service=mock_email,
    )

    analyzer.analyze("report.xml")

    assert mock_email.was_called is False


def test_analyze_does_not_send_email_for_valid_file(mock_email):
    class StubWebServiceThatSucceeds:
        def log_error(self, message: str) -> None:
            pass

    analyzer = LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=StubWebServiceThatSucceeds(),
        email_service=mock_email,
    )

    analyzer.analyze("system.log")

    assert mock_email.was_called is False
```

---

### 🤔 Step 5 — Identify Stub and Mock in Each Test

In each test, label the fakes with a comment:

```python
# web_service=StubWebServiceThatFails()  → STUB (simulates failure, not asserted)
# email_service=mock_email               → MOCK (asserted at the end)
```

---

### ▶️ Step 6 — Run Your Tests

```bash
pytest -v
```

All tests must pass. Then deliberately break the fallback logic in `analyze` (remove the `except` block) and confirm the relevant tests go red.

Restore the code before submitting.

---

## 📦 Deliverable

1. `email_service.py` — `EmailService` protocol + `SmtpEmailService`
2. `log_analyzer.py` — `LogAnalyzer` with three-dependency constructor and fallback email logic
3. `extension_manager.py`, `web_service.py` — unchanged from UT-05
4. `test_log_analyzer.py` — `StubWebServiceThatFails`, `MockEmailService`, at least **5 tests**, stub/mock labels in comments
5. All tests passing with `pytest -v`

---

> 🏗️ *Writing stubs and mocks by hand builds the mental model — you understand exactly what is being faked and why. In UT-07 you replace all of this handwritten code with a single import: `pytest-mock`.*
