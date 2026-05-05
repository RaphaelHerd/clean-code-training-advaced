# 🧪 Lab UT-03 — Breaking Dependencies with Stubs

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Stubs · Dependency Inversion · Interface Extraction &nbsp;|&nbsp; 📐 Artifacts: `log_analyzer.py` · `extension_manager.py` · `test_log_analyzer.py`

---

## 📖 Context

The `LogAnalyzer` from UT-01 had its valid extensions hardcoded. In a real system, those extensions come from a configuration file on disk. The moment you add that file read, your test stops being a unit test — it becomes an integration test that can fail because of a missing file, a wrong path, or a permission error, even though the logic inside `LogAnalyzer` is perfectly correct.

This is called a **test-inhibiting design**: the code has a dependency on an external resource that can break the test even when the code's logic is valid.

The fix is a **stub** — a controllable replacement for the real dependency. To plug in a stub, you first need a seam: an interface that both the real implementation and the stub satisfy. In this lab you extract that interface using Python's `Protocol`, write a handwritten stub, and inject it so your tests never touch the filesystem.

---

## ✅ Your Tasks

### 📁 Step 1 — Create the New Application Under Test

This version of `LogAnalyzer` loads its valid extensions from a file via an `ExtensionManager`. Create both files exactly as shown.

```python
# extension_manager.py

class FileExtensionManager:
    """Reads the list of valid extensions from a plain text file (one per line)."""

    def get_managed_extension_list(self) -> list[str]:
        with open("extensions.txt") as f:
            return [line.strip() for line in f if line.strip()]
```

```python
# log_analyzer.py

from extension_manager import FileExtensionManager


class LogAnalyzer:
    def __init__(self):
        self._manager = FileExtensionManager()

    def is_valid_log_file_name(self, filename: str) -> bool:
        if not filename:
            raise ValueError("Filename cannot be empty")
        extension = filename[filename.rfind("."):]
        return extension in self._manager.get_managed_extension_list()
```

Create `extensions.txt` in the same folder:

```
.log
.txt
```

Run it manually to confirm it works:

```python
from log_analyzer import LogAnalyzer
analyzer = LogAnalyzer()
print(analyzer.is_valid_log_file_name("system.log"))  # True
```

---

### 🔍 Step 2 — Write a Test That Reveals the Problem

Write a test for `is_valid_log_file_name` exactly as you did in UT-01:

```python
def test_is_valid_log_file_name_log_extension_returns_true():
    analyzer = LogAnalyzer()
    result = analyzer.is_valid_log_file_name("system.log")
    assert result is True
```

Now delete (or rename) `extensions.txt` and run the test again. Observe the error — it is a filesystem error, not a logic error. This is the integration test problem.

Restore `extensions.txt` before continuing.

---

### 🔌 Step 3 — Extract an Interface Using `Protocol`

Python's `typing.Protocol` lets you define a structural interface without inheritance. Any class that has the right method signature satisfies the protocol automatically.

Create the protocol in `extension_manager.py`:

```python
# extension_manager.py

from typing import Protocol


class ExtensionManager(Protocol):
    def get_managed_extension_list(self) -> list[str]:
        ...


class FileExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        with open("extensions.txt") as f:
            return [line.strip() for line in f if line.strip()]
```

---

### 🔧 Step 4 — Refactor `LogAnalyzer` to Accept the Interface

Change `LogAnalyzer` so it receives any `ExtensionManager`-compatible object through its constructor instead of creating a `FileExtensionManager` internally:

```python
# log_analyzer.py

from extension_manager import ExtensionManager


class LogAnalyzer:
    def __init__(self, manager: ExtensionManager):
        self._manager = manager

    def is_valid_log_file_name(self, filename: str) -> bool:
        if not filename:
            raise ValueError("Filename cannot be empty")
        extension = filename[filename.rfind("."):]
        return extension in self._manager.get_managed_extension_list()
```

> 💡 **Tip:** This is **constructor injection** — the dependency is injected at construction time. The class no longer decides *which* implementation to use; its caller does. This is the seam that makes stubs possible.

---

### 🧱 Step 5 — Write a Handwritten Stub

A stub is a controllable replacement that always returns a fixed, predictable value. Write it in your test file:

```python
# test_log_analyzer.py

class StubExtensionManager:
    """Always reports .log and .txt as valid — no filesystem involved."""

    def get_managed_extension_list(self) -> list[str]:
        return [".log", ".txt"]
```

Notice: `StubExtensionManager` satisfies `ExtensionManager` simply by having the right method — no explicit inheritance needed.

---

### 🧪 Step 6 — Inject the Stub in Your Tests

```python
import pytest
from log_analyzer import LogAnalyzer


class StubExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        return [".log", ".txt"]


@pytest.fixture
def analyzer():
    return LogAnalyzer(manager=StubExtensionManager())


def test_is_valid_log_file_name_log_extension_returns_true(analyzer):
    result = analyzer.is_valid_log_file_name("system.log")
    assert result is True


def test_is_valid_log_file_name_txt_extension_returns_true(analyzer):
    result = analyzer.is_valid_log_file_name("report.txt")
    assert result is True


def test_is_valid_log_file_name_xml_extension_returns_false(analyzer):
    result = analyzer.is_valid_log_file_name("config.xml")
    assert result is False
```

Delete `extensions.txt` and run `pytest -v`. All tests must pass — the suite no longer depends on the filesystem.

---

### ▶️ Step 7 — Run and Verify

```bash
pytest -v
```

All tests pass even without `extensions.txt` on disk. That is the proof that your tests are now true unit tests.

---

## 📦 Deliverable

1. `extension_manager.py` — `ExtensionManager` protocol + `FileExtensionManager` implementation
2. `log_analyzer.py` — refactored to accept any `ExtensionManager` via constructor
3. `test_log_analyzer.py` — `StubExtensionManager` + at least **5 tests**, none touching the filesystem
4. All tests passing with `pytest -v` even when `extensions.txt` is absent

---

> 🏗️ *The seam you created here — the `ExtensionManager` protocol and constructor injection — is the same pattern used for every other dependency in the next three labs: web services, email clients, databases.*
