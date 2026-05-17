# 🧪 Lab UT-02 — Setup and Teardown

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Unit Testing · Fixtures · Setup · Teardown &nbsp;|&nbsp; 📐 Artifacts: `log_analyzer.py` · `test_log_analyzer.py`

---

## 📖 Context

When several tests share the same preparation code — creating the same object, opening the same resource — duplicating it in every test is noise. pytest gives you two mechanisms to eliminate that noise: `setup_method` / `teardown_method` for class-based tests, and `@pytest.fixture` for function-based tests.

But shared setup also introduces a risk: one test can silently contaminate the state seen by the next. In this lab you learn when shared setup helps, when it harms, and how to choose between the two approaches.

You continue with the same `LogAnalyzer` from UT-01.

---

## ✅ Your Tasks

### 📁 Step 1 — Start From Your UT-01 Tests

Copy your `log_analyzer.py` and `test_log_analyzer.py` from `ut-01/` into this folder. Your starting point is the test suite you wrote there.

---

### 🔍 Step 2 — Identify the Repeated Setup

Look at your tests. Every single one starts with:

```python
analyzer = LogAnalyzer()
```

This is repeated setup. It is harmless here because `LogAnalyzer` holds no mutable state — but in a larger suite it becomes maintenance overhead.

---

### 🏗️ Step 3 — Refactor to `setup_method` (Class-Based)

Wrap your tests inside a class and move the repeated construction into `setup_method`. pytest calls `setup_method` automatically before each test method.

```python
# test_log_analyzer.py

import pytest
from log_analyzer import LogAnalyzer


class TestLogAnalyzer:

    def setup_method(self):
        self.analyzer = LogAnalyzer()

    def test_is_valid_log_file_name_log_extension_returns_true(self):
        result = self.analyzer.is_valid_log_file_name("system.log")
        assert result is True

    def test_is_valid_log_file_name_txt_extension_returns_false(self):
        result = self.analyzer.is_valid_log_file_name("readme.txt")
        assert result is False

    # migrate the rest of your tests here ...
```

Run `pytest -v` and confirm all tests still pass.

---

### 🧹 Step 4 — Add `teardown_method`

`teardown_method` runs after each test, even if the test fails. It is the right place to release resources (close files, disconnect from databases, delete temporary files).

Add a teardown that prints which test just ran — useful for understanding the execution order:

```python
    def teardown_method(self, method: pytest.Function):
        print(f"\n[teardown] finished: {method.__name__}")
```

Run with `pytest -v -s` (the `-s` flag disables output capture so you can see the prints).

> 💡 **Tip:** For `LogAnalyzer` teardown is unnecessary because there are no resources to release. It is shown here only so you can observe the lifecycle.

---

### 🔧 Step 5 — Refactor to `@pytest.fixture` (Function-Based)

pytest fixtures are the modern, preferred alternative. They are more composable and work without classes.

Rewrite the same tests using a fixture:

```python
import pytest
from log_analyzer import LogAnalyzer


@pytest.fixture
def analyzer():
    return LogAnalyzer()


def test_is_valid_log_file_name_log_extension_returns_true(analyzer):
    result = analyzer.is_valid_log_file_name("system.log")
    assert result is True


def test_is_valid_log_file_name_txt_extension_returns_false(analyzer):
    result = analyzer.is_valid_log_file_name("readme.txt")
    assert result is False
```

Notice that `analyzer` is injected by name into each test function — you never call the fixture directly.

> 💡 **Tip:** A fixture can also perform teardown using `yield` instead of `return`. Everything after `yield` runs as teardown:
>
> ```python
> @pytest.fixture
> def analyzer():
>     a = LogAnalyzer()
>     yield a
>     # teardown code here (runs after each test)
> ```

---

### 🤔 Step 6 — Decide When Shared Setup Is Wrong

Consider this scenario: you modify `VALID_EXTENSIONS` inside a test and the next test sees the modified list. Simulate it:

```python
def test_add_extension_affects_next_test_antipattern(analyzer):
    analyzer.VALID_EXTENSIONS.append(".xml")
    result = analyzer.is_valid_log_file_name("config.xml")
    assert result is True

def test_xml_should_not_be_valid(analyzer):
    # This should return False — but does it?
    result = analyzer.is_valid_log_file_name("config.xml")
    assert result is False
```

Run these two tests and observe the result. Then answer: **does the fixture protect you from test contamination here, and why?**

Write your answer as a comment at the bottom of `test_log_analyzer.py`.

---

### ▶️ Step 7 — Final Run

```bash
pytest -v
```

All tests must pass. Confirm that `setup_method` and fixture produce identical behaviour.

---

## 📦 Deliverable

1. `log_analyzer.py` — unchanged from UT-01
2. `test_log_analyzer.py` — all UT-01 tests migrated to both class-based (`setup_method`) and fixture-based styles, plus the contamination experiment from Step 6
3. A comment at the bottom of the test file answering the contamination question
4. All tests passing with `pytest -v`

---

> 🏗️ *Shared setup keeps tests readable. The fixture you wrote here will be reused and extended in UT-03 when a real external dependency enters the picture.*
