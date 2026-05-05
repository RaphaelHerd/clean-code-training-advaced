# 🧪 Lab UT-04 — Injection Techniques

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Constructor Injection · Property Injection · Dependency Injection &nbsp;|&nbsp; 📐 Artifacts: `log_analyzer.py` · `extension_manager.py` · `test_log_analyzer.py`

---

## 📖 Context

In UT-03 you used **constructor injection** to plug a stub into `LogAnalyzer`. Constructor injection is the most common and most explicit technique — but it is not always the right choice. Sometimes a dependency is optional, or a sensible default should be used unless the caller explicitly overrides it.

In this lab you compare two injection techniques side by side:

| Technique | When to use |
|---|---|
| **Constructor injection** | Dependency is required — the class cannot function without it |
| **Property injection** | Dependency is optional — a default exists and the caller overrides it only when needed |

You work with the same `LogAnalyzer` and `ExtensionManager` from UT-03.

---

## ✅ Your Tasks

### 📁 Step 1 — Copy Your Files From UT-03

Copy `log_analyzer.py`, `extension_manager.py`, and `test_log_analyzer.py` from `ut-03/` into this folder as your starting point.

---

### 🏗️ Step 2 — Review Constructor Injection (UT-03 Style)

The current `LogAnalyzer` already uses constructor injection:

```python
class LogAnalyzer:
    def __init__(self, manager: ExtensionManager):
        self._manager = manager
```

The caller **must** supply a manager — there is no default. This is appropriate because `LogAnalyzer` cannot do anything without knowing which extensions are valid.

Write a test that shows what happens when you forget to pass the argument:

```python
def test_constructor_requires_manager():
    import pytest
    with pytest.raises(TypeError):
        LogAnalyzer()  # missing required argument
```

Run it — it must pass.

---

### 🔧 Step 3 — Introduce Property Injection

Now imagine a second optional dependency: a `Logger` that records what the analyzer does. Most tests do not care about logging — they should not be forced to supply a logger. Property injection is the right tool.

Extend `log_analyzer.py`:

```python
# log_analyzer.py

from typing import Protocol
from extension_manager import ExtensionManager


class Logger(Protocol):
    def log(self, message: str) -> None:
        ...


class NullLogger:
    """Default logger that silently discards all messages."""
    def log(self, message: str) -> None:
        pass


class LogAnalyzer:
    def __init__(self, manager: ExtensionManager):
        self._manager = manager
        self._logger: Logger = NullLogger()  # safe default

    @property
    def logger(self) -> Logger:
        return self._logger

    @logger.setter
    def logger(self, value: Logger) -> None:
        self._logger = value

    def is_valid_log_file_name(self, filename: str) -> bool:
        if not filename:
            raise ValueError("Filename cannot be empty")
        extension = filename[filename.rfind("."):]
        valid = extension in self._manager.get_managed_extension_list()
        self._logger.log(f"Checked '{filename}': {'valid' if valid else 'invalid'}")
        return valid
```

---

### 🧱 Step 4 — Write a Stub Logger

```python
# test_log_analyzer.py (add this stub)

class StubLogger:
    """Captures log messages so tests can inspect them."""

    def __init__(self):
        self.messages: list[str] = []

    def log(self, message: str) -> None:
        self.messages.append(message)
```

---

### 🧪 Step 5 — Write Tests for Both Injection Points

```python
import pytest
from log_analyzer import LogAnalyzer
from extension_manager import FileExtensionManager


class StubExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        return [".log"]


class StubLogger:
    def __init__(self):
        self.messages: list[str] = []

    def log(self, message: str) -> None:
        self.messages.append(message)


@pytest.fixture
def analyzer():
    return LogAnalyzer(manager=StubExtensionManager())


# --- Constructor injection ---

def test_constructor_requires_manager():
    with pytest.raises(TypeError):
        LogAnalyzer()


def test_valid_file_returns_true_without_custom_logger(analyzer):
    # No logger injected — NullLogger is used transparently
    result = analyzer.is_valid_log_file_name("system.log")
    assert result is True


# --- Property injection ---

def test_logger_receives_message_when_valid_file_checked(analyzer):
    stub_logger = StubLogger()
    analyzer.logger = stub_logger  # property injection

    analyzer.is_valid_log_file_name("system.log")

    assert len(stub_logger.messages) == 1
    assert "system.log" in stub_logger.messages[0]


def test_logger_message_contains_invalid_when_extension_unknown(analyzer):
    stub_logger = StubLogger()
    analyzer.logger = stub_logger

    analyzer.is_valid_log_file_name("report.csv")

    assert "invalid" in stub_logger.messages[0]
```

---

### 🤔 Step 6 — Compare the Two Techniques

Answer these questions as comments at the bottom of `test_log_analyzer.py`:

```python
# COMPARISON
# 1. Why is manager injected via the constructor but logger via a property?
# 2. What would break if you made manager optional (with a default FileExtensionManager)?
# 3. When would you choose property injection even for a required dependency?
```

---

### ▶️ Step 7 — Run Your Tests

```bash
pytest -v
```

All tests must pass.

---

## 📦 Deliverable

1. `log_analyzer.py` — `LogAnalyzer` with constructor injection for `manager` and property injection for `logger`, plus `NullLogger`
2. `extension_manager.py` — unchanged from UT-03
3. `test_log_analyzer.py` — stubs for both dependencies, at least **6 tests**, and the comparison comment block
4. All tests passing with `pytest -v`

---

> 🏗️ *You now have two seams in `LogAnalyzer` — one mandatory, one optional. In UT-05 a third dependency enters: a web service that must be called when an invalid file is detected. That one will introduce a new testing concept: the mock.*
