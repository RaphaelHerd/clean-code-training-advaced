# 🧪 Lab PB-01 — From Examples to Properties

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Property-Based Testing · Hypothesis · @given · Strategies &nbsp;|&nbsp; 📐 Artifacts: `calculator.py` · `test_calculator.py`

---

## 📖 Context

Example-based testing checks one specific input at a time: you pick values you can think of, run the code, and assert the result. It works — but it only proves the code is correct for the inputs *you happened to choose*.

Property-based testing flips this around. Instead of picking inputs, you describe a **property** that must hold for *any* valid input, and the framework — **Hypothesis** — generates hundreds of random inputs to try to break it. If it finds a failing case, it automatically shrinks it to the smallest possible input that still fails.

In this lab you start with example-based tests for a simple `add` function, watch them fail to catch a bug, then rewrite them as properties that catch it immediately.

---

## 📦 Setup

```bash
pip install hypothesis pytest
```

---

## ✅ Your Tasks

### 📁 Step 1 — Create the Application Under Test

```python
# calculator.py

def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b
```

---

### 🧪 Step 2 — Write Classical Example-Based Tests

Create `test_calculator.py` with a few handpicked examples:

```python
# test_calculator.py

from calculator import add


def test_add_two_positive_numbers():
    assert add(1, 2) == 3

def test_add_zero():
    assert add(5, 0) == 5

def test_add_negative_numbers():
    assert add(-3, -2) == -5

def test_add_positive_and_negative():
    assert add(10, -4) == 6
```

Run `pytest -v`. All pass.

---

### 🐛 Step 3 — Introduce a Bug That Passes All Examples

Replace the body of `add` with this broken implementation:

```python
def add(a: int, b: int) -> int:
    if a == 0:
        return 0   # wrong: add(0, b) should return b
    return a + b
```

Run `pytest -v` again. All four tests still pass, because none of the examples uses `0` as the first argument.

> 💡 **This is the core problem with example-based testing:** you can only find bugs you thought to look for.

---

### 🔬 Step 4 — Write Your First Hypothesis Property

Restore the correct `add` implementation first, then add a property-based test:

```python
# calculator.py
def add(a: int, b: int) -> int:
    return a + b
```

```python
# test_calculator.py

from hypothesis import given
from hypothesis import strategies as st
from calculator import add

@given(st.integers(), st.integers())
def test_add_commutativity(a: int, b: int):
    # Changing the order of arguments should not change the result
    assert add(a, b) == add(b, a)
```

Run `pytest -v`. Hypothesis will generate 100 random integer pairs and check the property for each one.

Now introduce the buggy implementation again:

```python
def add(a: int, b: int) -> int:
    if a == 0:
        return 0
    return a + b
```

Run the test. Hypothesis will find a counterexample and report it. Read the output carefully:

```
Falsifying example: test_add_commutativity(a=0, b=1)
```

Hypothesis not only found a failing case — it **shrunk** the input to the smallest integers that expose the bug.

---

### 🏗️ Step 5 — Write Three More Properties

Restore the correct implementation and write three additional properties. Use these mathematical rules as a guide:

| Property | Rule | Hint |
|---|---|---|
| **Associativity** | `add(add(a, b), c) == add(a, add(b, c))` | Three integers |
| **Identity** | `add(a, 0) == a` | One integer, second fixed to `0` |
| **Additive** | `add(a, 2) == add(add(a, 1), 1)` | One integer, checks increment by steps |

```python
@given(st.integers(), st.integers(), st.integers())
def test_add_associativity(a, b, c):
    assert add(add(a, b), c) == add(a, add(b, c))


@given(st.integers())
def test_add_identity(a):
    assert add(a, 0) == a


@given(st.integers())
def test_add_additive_property(a):
    assert add(add(a, 1), 1) == add(a, 2)
```

Run `pytest -v`. All must pass.

---

### 🤔 Step 6 — Understand What Hypothesis Is Doing

Hypothesis does not truly pick random numbers. It uses a **database of previously found failures** and a set of **strategies** — generators that know how to produce interesting values.

Add this to one test and rerun to see what Hypothesis actually generates:

```python
from hypothesis import Verbosity, given, settings
from hypothesis import strategies as st

@settings(max_examples=10, verbosity=Verbosity.verbose)
@given(st.integers(min_value=-100, max_value=100), st.integers(min_value=-100, max_value=100))
def test_add_commutativity_verbose(a, b):
    assert add(a, b) == add(b, a)
```

Run pytest with output capture disabled so the generated examples are printed:

```bash
pytest -v -s
```

Observe: Hypothesis always tries `0`, `1`, `-1`, and extreme values before moving to arbitrary ones. These are the **boundary cases** it knows are most likely to break code.

---

### 📊 Step 7 — Compare the Two Approaches

Fill in this comparison at the bottom of `test_calculator.py`:

```python
# EXAMPLE-BASED vs. PROPERTY-BASED
# ┌────────────────────────────────┬──────────────────────┬───────────────────────┐
# │ Question                       │ Example-Based        │ Property-Based        │
# ├────────────────────────────────┼──────────────────────┼───────────────────────┤
# │ Who chooses the inputs?        │                      │                       │
# │ How many cases are tested?     │                      │                       │
# │ Can it find unexpected bugs?   │                      │                       │
# │ What do you assert?            │                      │                       │
# │ What happens when it fails?    │                      │                       │
# └────────────────────────────────┴──────────────────────┴───────────────────────┘
```

---

### ▶️ Step 8 — Final Run

```bash
pytest -v
```

All tests must pass.

---

## 📦 Deliverable

1. `calculator.py` — correct `add` implementation
2. `test_calculator.py` — 4 example-based tests + 4 property-based tests using `@given`, plus the comparison table
3. All tests passing with `pytest -v`

---

> 🏗️ *You now know the fundamental idea: properties describe rules, Hypothesis breaks them. In PB-04 you apply this to a real domain object — a shopping basket — where the properties reflect actual business rules your team would care about.*
