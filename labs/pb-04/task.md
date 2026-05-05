# 🧪 Lab PB-04 — Basket Invariants

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Property-Based Testing · Custom Strategies · @composite · Domain Invariants &nbsp;|&nbsp; 📐 Artifacts: `basket.py` · `test_basket.py`

---

## 📖 Context

In PB-01 you tested a pure function with integers — a deliberately simple case. In daily work, the objects you need to test are domain classes: a `Basket`, an `Order`, a `UserAccount`. These have multiple fields, internal rules, and operations that must preserve certain guarantees regardless of the data inside.

Those guarantees are called **invariants** — conditions that must be true before *and* after every operation, for any valid input. Property-based testing is the ideal tool for verifying invariants because it generates arbitrary inputs automatically.

But Hypothesis cannot know what a valid `Basket` looks like. You have to teach it — using a **custom strategy** built with `@composite`. This is the single most important skill for applying PBT to real code.

---

## 📦 Setup

```bash
pip install hypothesis pytest
```

---

## ✅ Your Tasks

### 📁 Step 1 — Create the Application Under Test

```python
# basket.py

from dataclasses import dataclass, field


@dataclass
class Item:
    name: str
    price: float


class Basket:
    def __init__(self):
        self._items: list[Item] = []

    def add_item(self, name: str, price: float) -> None:
        """Add an item to the basket."""
        if price < 0:
            raise ValueError(f"Price cannot be negative: {price}")
        self._items.append(Item(name=name, price=price))

    def remove_item(self, name: str) -> None:
        """Remove all items with the given name. No-op if name is not in basket."""
        self._items = [i for i in self._items if i.name != name]

    def total(self) -> float:
        """Return the sum of all item prices."""
        return sum(i.price for i in self._items)

    def item_names(self) -> list[str]:
        """Return a list of all item names (with duplicates)."""
        return [i.name for i in self._items]

    def __len__(self) -> int:
        return len(self._items)
```

Explore it manually:

```python
from basket import Basket

b = Basket()
b.add_item("Milk", 1.09)
b.add_item("Bread", 0.89)
print(b.total())       # 1.98
print(len(b))          # 2
b.remove_item("Milk")
print(b.total())       # 0.89
```

---

### 🧪 Step 2 — Write Example-Based Tests First

Before writing properties, write two example-based tests to confirm the class works at all:

```python
# test_basket.py

from basket import Basket


def test_total_of_empty_basket_is_zero():
    basket = Basket()
    assert basket.total() == 0.0


def test_total_equals_sum_of_added_prices():
    basket = Basket()
    basket.add_item("Milk", 1.09)
    basket.add_item("Bread", 0.89)
    assert basket.total() == pytest.approx(1.98)
```

Run `pytest -v`. Both must pass.

---

### 🏗️ Step 3 — Build a Custom Strategy with `@composite`

Hypothesis cannot generate a `Basket` out of the box. Use `@composite` to define a strategy that builds one by drawing from simpler strategies:

```python
# test_basket.py (add below the imports)

import pytest
from hypothesis import given, assume
from hypothesis import strategies as st
from hypothesis.strategies import composite
from basket import Basket


@composite
def basket_strategy(draw):
    """Generate a Basket containing 0–8 items with realistic names and prices."""
    item_count = draw(st.integers(min_value=0, max_value=8))
    basket = Basket()
    for _ in range(item_count):
        name = draw(st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=1,
            max_size=15,
        ))
        price = draw(st.floats(
            min_value=0.0,
            max_value=500.0,
            allow_nan=False,
            allow_infinity=False,
        ))
        basket.add_item(name, round(price, 2))
    return basket
```

> 💡 **How `@composite` works:** The `draw` function pulls a value from a strategy and gives it to you. Each call to `draw` is independent — Hypothesis tracks all drawn values and shrinks them together when a failure is found.

Test the strategy by printing a few generated baskets:

```python
@given(basket_strategy())
def test_strategy_produces_valid_baskets(basket):
    # Confirm the strategy itself does not crash
    assert basket.total() >= 0.0
```

Run `pytest -v`. This should pass immediately.

---

### 🔒 Step 4 — Write the Invariant Properties

Now write a property for each invariant. Each one is a business rule that must hold for any basket Hypothesis can build.

#### Invariant 1 — Total Is Never Negative

```python
@given(basket_strategy())
def test_total_is_never_negative(basket):
    assert basket.total() >= 0.0
```

#### Invariant 2 — Adding an Item Increases the Total

```python
@given(basket_strategy(), st.floats(min_value=0.01, max_value=500.0, allow_nan=False, allow_infinity=False))
def test_adding_item_increases_total(basket, price):
    price = round(price, 2)
    total_before = basket.total()

    basket.add_item("NewItem", price)

    assert basket.total() > total_before
```

#### Invariant 3 — Total Equals the Sum of Individual Prices

```python
@given(basket_strategy())
def test_total_equals_sum_of_item_prices(basket):
    from basket import Item
    expected = sum(
        round(i.price, 2)
        for i in basket._items
    )
    assert basket.total() == pytest.approx(expected)
```

#### Invariant 4 — Removing an Unknown Item Leaves the Basket Unchanged

```python
@given(basket_strategy(), st.text(min_size=1))
def test_removing_unknown_item_does_not_change_basket(basket, name):
    assume(name not in basket.item_names())  # only run when name is truly absent

    total_before = basket.total()
    size_before = len(basket)

    basket.remove_item(name)

    assert basket.total() == pytest.approx(total_before)
    assert len(basket) == size_before
```

> 💡 **What `assume()` does:** It tells Hypothesis to discard the current example if the condition is false and try another. Use it sparingly — if too many examples are discarded Hypothesis will warn you.

#### Invariant 5 — Adding Then Removing an Item Restores the Original Total

```python
@given(basket_strategy(), st.text(min_size=1, max_size=15), st.floats(min_value=0.01, max_value=500.0, allow_nan=False, allow_infinity=False))
def test_add_then_remove_restores_total(basket, name, price):
    assume(name not in basket.item_names())
    price = round(price, 2)
    total_before = basket.total()

    basket.add_item(name, price)
    basket.remove_item(name)

    assert basket.total() == pytest.approx(total_before)
```

---

### 🐛 Step 5 — Introduce a Bug and Watch Hypothesis Find It

Change `total()` in `basket.py` to this subtly broken version:

```python
def total(self) -> float:
    if len(self._items) > 5:
        return sum(i.price for i in self._items[:-1])  # forgets the last item
    return sum(i.price for i in self._items)
```

Run `pytest -v`. Hypothesis will find a basket with more than 5 items where `total()` is wrong, then shrink it to the minimal failing case — likely exactly 6 items.

Read the shrunk counterexample from the output. Then restore the correct implementation:

```python
def total(self) -> float:
    return sum(i.price for i in self._items)
```

Run `pytest -v` — all tests green again.

---

### 🤔 Step 6 — Reflect

Answer these questions as a comment block at the bottom of `test_basket.py`:

```python
# REFLECTION
# 1. Which invariant would be hardest to find with example-based tests alone, and why?
# 2. What does `assume()` do, and what is the risk of overusing it?
# 3. Why did Hypothesis shrink the failing basket to exactly 6 items in Step 5?
# 4. Name one invariant of a class in your own codebase that could be expressed as a
#    Hypothesis property.
```

---

### ▶️ Step 7 — Final Run

```bash
pytest -v
```

All tests must pass with the correct `basket.py`.

---

## 📦 Deliverable

1. `basket.py` — `Item` dataclass + `Basket` class with `add_item`, `remove_item`, `total`, `item_names`
2. `test_basket.py` — `basket_strategy` composite strategy, 5 invariant properties, 2 example-based baseline tests, and the reflection comment block
3. All tests passing with `pytest -v`

---

> 🏗️ *The `@composite` pattern you used here scales to any domain object in your codebase. Whenever you can describe a rule that must always hold — regardless of the data — you have a candidate for a property test.*
