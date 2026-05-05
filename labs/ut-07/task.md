# 🧪 Lab UT-07 — Dynamic Fakes with pytest-mock

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Isolation Frameworks · pytest-mock · MagicMock · patch &nbsp;|&nbsp; 📐 Artifacts: `log_analyzer.py` · `test_log_analyzer.py`

---

## 📖 Context

In UT-03 through UT-06 you wrote every stub and mock by hand. That process is valuable — it forces you to understand what is being faked and why — but in a large codebase it produces a lot of repetitive boilerplate.

An **isolation framework** is a library that generates fake objects at runtime so you do not have to write them yourself. In the Python/pytest world that framework is **pytest-mock**, which wraps Python's `unittest.mock` and integrates it cleanly into the pytest fixture system.

In this lab you rewrite the handwritten fakes from UT-05 and UT-06 using `MagicMock` and `mocker.patch`, and you compare the two approaches.

---

## 📦 Setup

```bash
pip install pytest-mock
```

Copy `log_analyzer.py`, `extension_manager.py`, `web_service.py`, and `email_service.py` from UT-06 unchanged.

---

## ✅ Your Tasks

### 🧠 Step 1 — Understand `MagicMock`

`MagicMock` is a fake object that:
- Accepts any attribute access without raising `AttributeError`
- Records every method call automatically
- Returns another `MagicMock` for any call by default (configurable)

```python
from unittest.mock import MagicMock

service = MagicMock()
service.log_error("something")

# assert the call happened
service.log_error.assert_called_once()
service.log_error.assert_called_once_with("something")

# check call count
assert service.log_error.call_count == 1

# check arguments of the last call
assert service.log_error.call_args.args[0] == "something"
```

Run these in a Python REPL to build familiarity before writing tests.

---

### 🧪 Step 2 — Rewrite the UT-05 Tests Without Handwritten Mocks

In UT-05 you wrote `MockWebService` by hand. Replace it entirely with `MagicMock`:

```python
# test_log_analyzer.py

import pytest
from unittest.mock import MagicMock
from log_analyzer import LogAnalyzer


class StubExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        return [".log"]


@pytest.fixture
def web_service_mock():
    return MagicMock()


@pytest.fixture
def analyzer(web_service_mock):
    return LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=web_service_mock,
        email_service=MagicMock(),  # not the focus of these tests → stub role
    )


def test_analyze_invalid_extension_calls_log_error(analyzer, web_service_mock):
    analyzer.analyze("report.xml")

    web_service_mock.log_error.assert_called_once()


def test_analyze_invalid_extension_sends_filename_in_message(analyzer, web_service_mock):
    analyzer.analyze("report.xml")

    args = web_service_mock.log_error.call_args.args
    assert "report.xml" in args[0]


def test_analyze_valid_extension_does_not_call_log_error(analyzer, web_service_mock):
    analyzer.analyze("system.log")

    web_service_mock.log_error.assert_not_called()
```

---

### 🧪 Step 3 — Rewrite the UT-06 Tests (Stub + Mock)

Use `side_effect` to make a `MagicMock` raise an exception — turning it into a stub that simulates a failure:

```python
from unittest.mock import MagicMock
from log_analyzer import LogAnalyzer, ADMIN_EMAIL


@pytest.fixture
def email_mock():
    return MagicMock()


@pytest.fixture
def analyzer_with_failing_service(email_mock):
    failing_web_service = MagicMock()
    failing_web_service.log_error.side_effect = ConnectionError("unreachable")
    return LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=failing_web_service,   # stub via side_effect
        email_service=email_mock,          # mock
    )


def test_sends_email_when_web_service_fails(analyzer_with_failing_service, email_mock):
    analyzer_with_failing_service.analyze("report.xml")

    email_mock.send_email.assert_called_once()


def test_email_is_sent_to_admin(analyzer_with_failing_service, email_mock):
    analyzer_with_failing_service.analyze("report.xml")

    _, kwargs = email_mock.send_email.call_args
    assert kwargs["to"] == ADMIN_EMAIL


def test_no_email_when_web_service_succeeds(email_mock):
    working_service = MagicMock()  # does not raise
    analyzer = LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=working_service,
        email_service=email_mock,
    )

    analyzer.analyze("report.xml")

    email_mock.send_email.assert_not_called()
```

---

### 🔧 Step 4 — Use `mocker.patch` to Replace a Dependency at Import Time

`mocker.patch` is the pytest-mock fixture version of `unittest.mock.patch`. It temporarily replaces a name in a module's namespace for the duration of a single test.

This is useful when you cannot inject a dependency through the constructor — for example, when the class instantiates it internally.

Demonstrate `mocker.patch` by reverting `LogAnalyzer` to the UT-01 version (no injection), and patching `FileExtensionManager.get_managed_extension_list` directly:

```python
# For demonstration only — add this test at the bottom of the file

def test_patch_extension_manager_via_mocker(mocker):
    mocker.patch(
        "extension_manager.FileExtensionManager.get_managed_extension_list",
        return_value=[".log"],
    )

    from log_analyzer_no_injection import LogAnalyzer as BasicAnalyzer
    analyzer = BasicAnalyzer()
    result = analyzer.is_valid_log_file_name("system.log")

    assert result is True
```

> 💡 **Tip:** `mocker.patch` automatically restores the original after the test. Never use `unittest.mock.patch` without `mocker` in pytest — cleanup is not guaranteed.

---

### 📊 Step 5 — Compare Handwritten vs. Dynamic Fakes

Fill in this table as a comment at the top of `test_log_analyzer.py`:

```python
# HANDWRITTEN vs. DYNAMIC FAKES
# ┌────────────────────────────┬────────────────────────┬────────────────────────┐
# │ Property                   │ Handwritten            │ MagicMock              │
# ├────────────────────────────┼────────────────────────┼────────────────────────┤
# │ Lines of code per fake     │                        │                        │
# │ Explicit about interface?  │                        │                        │
# │ Catches typos in methods?  │                        │                        │
# │ Configurable return values │                        │                        │
# │ Can simulate exceptions?   │                        │                        │
# └────────────────────────────┴────────────────────────┴────────────────────────┘
```

---

### ▶️ Step 6 — Run Your Tests

```bash
pytest -v
```

All tests must pass.

---

## 📦 Deliverable

1. `log_analyzer.py`, `extension_manager.py`, `web_service.py`, `email_service.py` — unchanged from UT-06
2. `test_log_analyzer.py` — all UT-05 and UT-06 scenarios rewritten using `MagicMock` and `mocker.patch`, plus the comparison table
3. All tests passing with `pytest -v`

---

> 🏗️ *`MagicMock` is flexible but permissive — it accepts any call, even misspelled ones. In UT-08 you learn to restrict that permissiveness with strict mocks, so accidental typos in method names fail loudly instead of silently.*
