# 🧪 Lab UT-08 — Strict vs. Non-Strict Mocks

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Mock Strictness · spec · assert_called · Pitfalls &nbsp;|&nbsp; 📐 Artifacts: `log_analyzer.py` · `test_log_analyzer.py`

---

## 📖 Context

In UT-07 you used `MagicMock()` without any restrictions. The default `MagicMock` is **non-strict**: it accepts any attribute access or method call, even if that method does not exist on the real object. This is convenient but dangerous — a typo in a method name silently passes instead of raising an error.

A **strict mock** is created with `spec=SomeClass`. It only allows attribute access and calls that exist on the real class. Any unexpected access raises `AttributeError` immediately.

In this lab you explore both modes, observe where non-strict mocks hide bugs, and learn when to reach for `spec=`.

---

## 📦 Setup

Copy all files from UT-07. No new application code is needed.

---

## ✅ Your Tasks

### 🔍 Step 1 — Reproduce the Non-Strict Pitfall

With a plain `MagicMock`, a misspelled method name silently succeeds:

```python
from unittest.mock import MagicMock
from web_service import WebService


def test_nonstrict_mock_hides_typo():
    mock = MagicMock()

    # Simulate a caller with a typo
    mock.log_errror("oops")   # three r's — wrong method name

    # This passes even though log_error was never called
    assert mock.log_errror.called is True
    # But the real method was never triggered:
    mock.log_error.assert_not_called()
```

Run this test and observe that it passes — the typo is invisible. This is the non-strict pitfall.

---

### 🔧 Step 2 — Enforce a Strict Mock with `spec=`

Pass `spec=WebService` (or `spec=RealWebService`) when creating the mock. Now only methods that actually exist on `WebService` are accessible:

```python
from unittest.mock import MagicMock
from web_service import WebService


def test_strict_mock_rejects_typo():
    mock = MagicMock(spec=WebService)

    import pytest
    with pytest.raises(AttributeError):
        mock.log_errror("oops")   # raises — method does not exist on WebService
```

Run this test. It must pass — the strict mock catches the typo.

---

### 🧪 Step 3 — Rewrite Key Tests with Strict Mocks

Go back to the tests you wrote in UT-07 and add `spec=` to the mock fixtures that represent real classes. This makes the test suite safer without changing any test logic:

```python
from unittest.mock import MagicMock
from web_service import WebService
from email_service import EmailService


@pytest.fixture
def web_service_mock():
    return MagicMock(spec=WebService)


@pytest.fixture
def email_mock():
    return MagicMock(spec=EmailService)
```

Run `pytest -v`. All tests must still pass — strict mocks do not restrict *valid* calls, only invalid ones.

---

### ⚡ Step 4 — Explore `create_autospec`

`create_autospec` is stricter than `spec=` — it also validates the **arguments** of each call against the real method's signature:

```python
from unittest.mock import create_autospec
from web_service import WebService


def test_autospec_validates_argument_count():
    mock = create_autospec(WebService)

    import pytest
    with pytest.raises(TypeError):
        mock.log_error("first", "unexpected_second_arg")  # too many arguments
```

Try calling `mock.log_error("correct")` — it should succeed.

> 💡 **Tip:** `create_autospec` is particularly useful for interfaces with multiple methods and keyword arguments, where a plain `spec=` would not catch wrong-argument-count bugs.

---

### 🤔 Step 5 — Strict Mock Can Fail in Two Ways

A strict mock fails the test if:

1. An **expected method is never called** (you assert `assert_called_once()` but the code never called it)
2. An **unexpected method is called** (an attribute that does not exist on the spec is accessed)

Write one test demonstrating each failure mode:

```python
def test_strict_mock_fails_when_expected_call_is_missing():
    mock = MagicMock(spec=WebService)
    # Don't call mock.log_error at all

    with pytest.raises(AssertionError):
        mock.log_error.assert_called_once()


def test_strict_mock_fails_when_unexpected_method_is_called():
    mock = MagicMock(spec=WebService)

    with pytest.raises(AttributeError):
        mock.nonexistent_method()
```

---

### 📊 Step 6 — When to Use Which

Fill in this decision guide as a comment in `test_log_analyzer.py`:

```python
# WHEN TO USE WHICH MOCK TYPE
#
# MagicMock() (non-strict)
#   ✅ Use when: prototyping, the interface changes frequently, the fake has many methods
#              and you only care about a subset
#   ❌ Avoid when: method names are long or similar, wrong calls must be detected early
#
# MagicMock(spec=SomeClass) (strict)
#   ✅ Use when: the interface is stable, you want early detection of typos,
#              you are testing production code
#   ❌ Avoid when: the spec class has many abstract/private internals that MagicMock struggles with
#
# create_autospec(SomeClass) (strictest)
#   ✅ Use when: argument signatures matter and wrong argument counts must fail loudly
#   ❌ Avoid when: the overhead of argument checking slows down a large test suite significantly
```

---

### ▶️ Step 7 — Final Run

```bash
pytest -v
```

All tests must pass.

---

## 📦 Deliverable

1. `test_log_analyzer.py` — non-strict pitfall test, strict mock tests, `create_autospec` example, two failure-mode demonstrations, and the decision-guide comment block
2. All other files unchanged from UT-07
3. All tests passing with `pytest -v`

---

> 🏗️ *You have now worked through the full mock spectrum: handwritten → non-strict dynamic → strict → autospec. In UT-09 you close the workshop with TDD — the practice that makes all of these testing skills your default mode rather than an afterthought.*
