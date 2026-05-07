# 🧪 Lab UT-01 — Your First Unit Test

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Unit Testing · AAA Pattern · Naming · Exception Testing &nbsp;|&nbsp; 📐 Artifacts: `log_analyzer.py` · `test_log_analyzer.py`

---

## 📖 Context

A unit test is a piece of code that calls another piece of code and checks whether the result is what you expected. The key word is *unit* — one method, one behaviour, one assertion per test.

In this lab you receive a simple `LogAnalyzer` class that decides whether a filename has a recognized log extension. Your job is to write your first pytest test suite for it, applying three non-negotiable rules from the start: the **AAA pattern**, **meaningful test names**, and **exception testing**.

---

## ✅ Your Tasks

### 📦 Step 0 — Install pytest

Install the package into your Python environment:

```bash
pip install pytest
```

Verify the installation:

```bash
python -m pytest --version
```
> 💡 **Hint:** Its important to node that during this session you need to use **python -m pytest** instead of **pytest**.


### 📁 Step 1 — Create the Application Under Test

Create `log_analyzer.py` with the following content. Do not modify it yet — your job is to test it, not fix it.

```python
# log_analyzer.py

class LogAnalyzer:
    VALID_EXTENSIONS = [".log"]

    def is_valid_log_file_name(self, filename: str) -> bool:
        """Return True when the file's extension is in the allowed list."""
        if not filename:
            raise ValueError("Filename cannot be empty")
        extension = filename[filename.rfind("."):]
        return extension in self.VALID_EXTENSIONS
```

Explore it manually first:

```python
from log_analyzer import LogAnalyzer

analyzer = LogAnalyzer()
print(analyzer.is_valid_log_file_name("system.log"))  # True
print(analyzer.is_valid_log_file_name("readme.txt"))  # False
```

---

### 📝 Step 2 — Apply the Naming Convention

Every test name must answer three questions: **what is being tested**, **under what condition**, and **what is the expected result**.

Use this pattern:

```
test_<method>_<condition>_<expected_result>
```

| Method | Condition | Expected Result | Test Name |
|---|---|---|---|
| `is_valid_log_file_name` | `.log` extension | returns `True` | `test_is_valid_log_file_name_log_extension_returns_true` |
| `is_valid_log_file_name` | `.txt` extension | returns `False` | `test_is_valid_log_file_name_txt_extension_returns_false` |
| `is_valid_log_file_name` | empty string | raises `ValueError` | `test_is_valid_log_file_name_empty_filename_raises_value_error` |

> 💡 **Tip:** A test name containing the word "and" is a warning sign — it likely tests more than one thing.

---

### 🧪 Step 3 — Write Tests Using the AAA Pattern

Create `test_log_analyzer.py`. Structure every test in three clearly separated sections: **Arrange**, **Act**, **Assert**.

```python
# test_log_analyzer.py

import pytest
from log_analyzer import LogAnalyzer


def test_is_valid_log_file_name_log_extension_returns_true():
    # Arrange
    analyzer = LogAnalyzer()

    # Act
    result = analyzer.is_valid_log_file_name("system.log")

    # Assert
    assert result is True


def test_is_valid_log_file_name_txt_extension_returns_false():
    # Arrange
    analyzer = LogAnalyzer()

    # Act
    result = analyzer.is_valid_log_file_name("readme.txt")

    # Assert
    assert result is False
```

Add at least **three more tests** of your own. Think about: filenames with no extension, filenames with uppercase extensions, filenames with multiple dots.

> 💡 **Tip:** Never put the `assert` inside an `if` block — a condition that evaluates to `False` would silently pass the test instead of failing it.

---

### ⚠️ Step 4 — Test for Expected Exceptions

Use `pytest.raises` as a context manager to assert that a specific exception is raised under a specific condition:

```python
def test_is_valid_log_file_name_empty_filename_raises_value_error():
    # Arrange
    analyzer = LogAnalyzer()

    # Act / Assert
    with pytest.raises(ValueError):
        analyzer.is_valid_log_file_name("")
```

You can also assert the exception message:

```python
    with pytest.raises(ValueError, match="cannot be empty"):
        analyzer.is_valid_log_file_name("")
```

---

### ▶️ Step 5 — Run Your Tests

```bash
pytest -v
```

Expected output (your test names will appear):

```
test_log_analyzer.py::test_is_valid_log_file_name_log_extension_returns_true PASSED
test_log_analyzer.py::test_is_valid_log_file_name_txt_extension_returns_false PASSED
test_log_analyzer.py::test_is_valid_log_file_name_empty_filename_raises_value_error PASSED
...
```

All tests must be green before moving on.

---

## 📦 Deliverable

1. `log_analyzer.py` — the application under test, unmodified
2. `test_log_analyzer.py` — at least **5 tests** covering valid extensions, invalid extensions, edge cases, and exception handling, all using the AAA pattern and the naming convention
3. All tests passing with `pytest -v`

---

> 🏗️ *The `LogAnalyzer` you tested here is the foundation of the next four labs. A green test suite now means every future change has a safety net from day one.*
