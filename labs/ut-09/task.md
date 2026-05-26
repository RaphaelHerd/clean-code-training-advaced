# 🧪 Lab UT-09 — TDD: Red · Green · Refactor

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Test-Driven Development · Red-Green-Refactor · Incremental Design &nbsp;|&nbsp; 📐 Artifacts: `password_validator.py` · `test_password_validator.py`

---

## 📖 Context

Test-Driven Development reverses the usual order: you write a failing test **before** a single line of production code exists. Then you write the minimum code to make it pass. Then you clean up. Repeat.

This three-step cycle — **Red → Green → Refactor** — is not just a testing technique. It is a design technique. Because you can only write code that makes a specific test pass, you never write more than what is needed. The result is lean, testable code with a full safety net from the first line.

In this lab you build a `PasswordValidator` entirely through TDD. You will go through **three full cycles**, each one adding a new rule. You start with nothing — no `password_validator.py` file exists yet.

---

## 📖 The Rules of TDD

| Step | What you do | Constraint |
|---|---|---|
| 🔴 **Red** | Write one failing test | Do not write any production code yet |
| 🟢 **Green** | Write the minimum code to pass | Do not write more code than needed to go green |
| 🔵 **Refactor** | Improve the design | Do not change behaviour — tests must stay green |

> 💡 **Tip:** "Minimum code to pass" sometimes means returning a hardcoded value. That is intentional — the next test will force you to generalize.

---

## ✅ Your Tasks

### 🔴🟢🔵 Cycle 1 — Minimum Length

**Goal:** A password must be at least 8 characters long.

#### Red — Write a Failing Test

Create `test_password_validator.py`. `password_validator.py` does not exist yet.

```python
# test_password_validator.py

from password_validator import PasswordValidator


def test_password_shorter_than_8_chars_is_invalid():
    validator = PasswordValidator()
    result = validator.validate("abc123")
    assert result.is_valid is False
```

Run `pytest`. It should fail with `ModuleNotFoundError`. That is your red state.

#### Green — Write the Minimum Code

Create `password_validator.py` with the absolute minimum to make the test pass:

```python
# password_validator.py

from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


class PasswordValidator:
    def validate(self, password: str) -> ValidationResult:
        errors = list[str]()
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

Run `pytest`. Green.

#### Refactor

The code is already clean. Add a second test to triangulate before moving on:

```python
def test_password_of_exactly_8_chars_is_valid():
    validator = PasswordValidator()
    result = validator.validate("abcd1234")
    assert result.is_valid is True
```

Run `pytest`. Both must be green.

---

### 🔴🟢🔵 Cycle 2 — Uppercase Requirement

**Goal:** A password must contain at least one uppercase letter.

#### Red

```python
def test_password_without_uppercase_is_invalid():
    validator = PasswordValidator()
    result = validator.validate("abcd1234")
    assert result.is_valid is False
```

Run `pytest`. This test fails — `"abcd1234"` is currently considered valid. Red.

#### Green

Add the uppercase check to `validate` in `password_validator.py`:

```python
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
```

Run `pytest`. All tests green? Check — the Cycle 1 test `test_password_of_exactly_8_chars_is_valid` may now fail because `"abcd1234"` no longer passes. Fix it by choosing a password that satisfies both rules:

```python
def test_password_meeting_both_rules_is_valid():
    validator = PasswordValidator()
    result = validator.validate("Abcd1234")
    assert result.is_valid is True
```

Remove or update the old "exactly 8 chars" test if it now conflicts. Run `pytest`. All green.

#### Refactor

The `validate` method has two `if` blocks. Extract a private helper list for clarity if you think the code benefits — but only if the tests stay green.

---

### 🔴🟢🔵 Cycle 3 — Special Character Requirement

**Goal:** A password must contain at least one special character from `!@#$%^&*`.

#### Red

```python
def test_password_without_special_character_is_invalid():
    validator = PasswordValidator()
    result = validator.validate("Abcd1234")
    assert result.is_valid is False
```

Run `pytest`. Red.

#### Green

```python
    SPECIAL_CHARS = set("!@#$%^&*")
    if not any(c in SPECIAL_CHARS for c in password):
        errors.append("Password must contain at least one special character (!@#$%^&*)")
```

Update the "valid password" test to satisfy all three rules:

```python
def test_password_meeting_all_rules_is_valid():
    validator = PasswordValidator()
    result = validator.validate("Abcd123!")
    assert result.is_valid is True
```

Run `pytest`. All green.

#### Refactor

`SPECIAL_CHARS` is defined inside the method. Move it to a class constant. Run `pytest` to confirm nothing broke.

---

### 📋 Step 4 — Test the Error Messages

TDD does not only drive behaviour — it drives the interface. Add tests that assert the content of the `errors` list:

```python
def test_validate_returns_error_message_for_short_password():
    validator = PasswordValidator()
    result = validator.validate("Ab1!")
    assert any("8 characters" in e for e in result.errors)


def test_validate_returns_error_message_for_missing_uppercase():
    validator = PasswordValidator()
    result = validator.validate("abcd123!")
    assert any("uppercase" in e.lower() for e in result.errors)


def test_validate_returns_multiple_errors_when_multiple_rules_fail():
    validator = PasswordValidator()
    result = validator.validate("abc")  # too short, no uppercase, no special char
    assert len(result.errors) == 3
```

---

### 📊 Step 5 — Reflect on the TDD Process

Answer these questions as a comment at the bottom of `test_password_validator.py`:

```python
# REFLECTION
# 1. At what point did you feel forced to generalize beyond a hardcoded return value?
# 2. Did any test you wrote catch a regression introduced by a later cycle? Which one?
# 3. What is the difference between writing tests after code vs. before code
#    in terms of the design decisions you made?
# 4. When would you NOT use TDD? Give one concrete scenario.
```

---

### ▶️ Step 6 — Final Run

```bash
pytest -v
```

All tests must be green. Count them — you should have at least **10 tests** covering all three validation rules, error messages, combined failures, and valid passwords.

---

## 📦 Deliverable

1. `password_validator.py` — `ValidationResult` dataclass + `PasswordValidator` built entirely through TDD, with all three rules
2. `test_password_validator.py` — at least **10 tests** covering all rules, edge cases, error messages, and the reflection comment block
3. All tests passing with `pytest -v`

---

> 🏗️ *TDD is not about tests — it is about design. Every lab in this workshop gave you a class to test. In the real world TDD means you never receive a class without tests: you write both, simultaneously, from nothing.*
