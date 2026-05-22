# 🧪 Lab FT-02 — Mutation Testing with mutmut

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Mutation Testing · Test Quality · Mutation Score · Coverage vs. Mutation &nbsp;|&nbsp; 📐 Artifacts: `route_calculator.py` · `test_route_calculator.py` · `setup.cfg`

---

## 📖 Context

100 % line coverage does not mean your tests are good. It only means every line was *executed* at least once. A line can run and still contain a bug your test never detects.

**Mutation testing** measures test quality differently: it makes hundreds of small, deliberate changes to your production code — **mutants** — and checks whether your tests catch each one. A mutant that survives means your tests would not notice if a developer accidentally introduced that exact change. That is a gap in your safety net.

In this lab you work with the **bug-free** version of the Route Calculator from FT-01. The code is correct — your mission is not to find crashes but to verify that your test suite is strong enough to detect any future accidental change to the logic.

---

## 📦 Setup

```bash
pip install pytest pytest-cov mutmut
```

---

## ✅ Your Tasks

### 📁 Step 1 — Create the Application Under Test

This is the **bug-free** version of the route calculator. Copy it exactly.

```python
# route_calculator.py

LOCATIONS = {
    "Berlin":    {"Hamburg": 288, "Munich": 585, "Frankfurt": 545},
    "Hamburg":   {"Berlin": 288, "Frankfurt": 490},
    "Munich":    {"Berlin": 585, "Frankfurt": 390, "Stuttgart": 220},
    "Frankfurt": {"Berlin": 545, "Hamburg": 490, "Munich": 390, "Stuttgart": 200},
    "Stuttgart": {"Munich": 220, "Frankfurt": 200},
}


def parse_route_request(request: str):
    """Parse a colon-separated route request: 'ORIGIN:DESTINATION:SPEED_KMH'"""
    parts = request.split(":")
    if len(parts) != 3:
        raise ValueError(f"Expected format 'ORIGIN:DESTINATION:SPEED', got: '{request}'")
    origin      = parts[0].strip()
    destination = parts[1].strip()
    speed       = int(parts[2].strip())
    if speed <= 0:
        raise ValueError(f"Speed must be positive, got: {speed}")
    return origin, destination, speed


def get_distance(origin: str, destination: str) -> int:
    """Return the direct distance (km) between two directly connected locations."""
    if origin not in LOCATIONS:
        raise ValueError(f"Unknown location: '{origin}'")
    if destination not in LOCATIONS[origin]:
        raise ValueError(f"No direct connection from '{origin}' to '{destination}'")
    return LOCATIONS[origin][destination]


def calculate_travel_time(distance: int, speed: int) -> float:
    """Return travel time in hours."""
    if speed <= 0:
        raise ValueError("Speed must be positive")
    return distance / speed


def find_route(origin: str, destination: str) -> list[str]:
    """BFS shortest-hop path. Returns empty list if no route exists."""
    if origin not in LOCATIONS or destination not in LOCATIONS:
        raise ValueError(f"Unknown location: '{origin}' or '{destination}'")
    if origin == destination:
        return [origin]

    visited = set[str]()
    queue   = [(origin, [origin])]

    while queue:
        current, path = queue.pop(0)
        if current == destination:
            return path
        if current in visited:
            continue
        visited.add(current)
        for neighbor in LOCATIONS.get(current, {}):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return []


def get_route_summary(request: str) -> str:
    """
    Full pipeline: parse request → find route → compute distance & time.
    Input format: 'ORIGIN:DESTINATION:SPEED_KMH'
    """
    origin, destination, speed = parse_route_request(request)
    route = find_route(origin, destination)

    if not route:
        raise ValueError(f"No route found from '{origin}' to '{destination}'")

    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += get_distance(route[i], route[i + 1])

    travel_time = calculate_travel_time(total_distance, speed)
    return (
        f"Route: {' -> '.join(route)} | "
        f"Distance: {total_distance} km | "
        f"Time: {travel_time:.2f} h at {speed} km/h"
    )
```

---

### ⚙️ Step 2 — Configure mutmut

Create `setup.cfg` so mutmut knows which file to mutate and which tests to run:

```ini
[mutmut]
paths_to_mutate=route_calculator.py
runner=python -m pytest
tests_dir=.
```

---

### 📝 Step 3 — Write a Baseline Test Suite

Before running mutmut you need tests. Write `test_route_calculator.py` covering the happy path for each function. Do not try to be thorough yet — just get the basics working.

```python
# test_route_calculator.py

import pytest
from route_calculator import (
    parse_route_request,
    get_distance,
    calculate_travel_time,
    find_route,
    get_route_summary,
)


def test_parse_valid_request():
    origin, destination, speed = parse_route_request("Berlin:Munich:120")
    assert origin == "Berlin"
    assert destination == "Munich"
    assert speed == 120

# TODO: add at least 2 more tests for parse_route_request (error cases)


def test_get_distance_direct_connection():
    assert get_distance("Berlin", "Hamburg") == 288

# TODO: add at least 2 more tests for get_distance (error cases)


def test_calculate_travel_time_basic():
    assert calculate_travel_time(288, 120) == pytest.approx(2.4)

# TODO: add at least 1 more test for calculate_travel_time (error case)


def test_find_route_direct_neighbour():
    route = find_route("Berlin", "Hamburg")
    assert route[0] == "Berlin"
    assert route[-1] == "Hamburg"

def test_find_route_same_location():
    assert find_route("Berlin", "Berlin") == ["Berlin"]

# TODO: add at least 2 more tests for find_route (multi-hop, error cases)


def test_get_route_summary_contains_cities():
    result = get_route_summary("Berlin:Hamburg:100")
    assert "Berlin" in result
    assert "Hamburg" in result

# TODO: add at least 3 more tests for get_route_summary
```

Confirm the baseline suite passes before moving on:

```bash
pytest -q
```

---

### ▶️ Step 4 — Run mutmut

```bash
mutmut run
```

mutmut applies one small change at a time, runs your full test suite against each mutant, and marks it **killed** (tests caught it) or **survived** (tests missed it). This takes a minute or two. The progress icons mean:

| Icon | Meaning |
|---|---|
| 🎉 | Killed — your tests caught the mutation |
| 🙈 | Survived — your tests did NOT catch it |
| ⏰ | Timed out |
| 🤔 | Suspicious (inconclusive) |

---

### 🔍 Step 5 — Read the Results

```bash
mutmut results
mutmut show
```

Check your initial **mutation score**. A typical first run with a thin test suite yields around **40–60 %**. Your target is **≥ 85 %**.

---

### 🔬 Step 6 — Inspect Surviving Mutants

For each surviving mutant, see exactly what was changed:

```bash
mutmut show <ID>
```

Example output:

```diff
--- route_calculator.py
+++ route_calculator.py (mutant 7)
@@ -38,7 +38,7 @@
-    return distance / speed
+    return distance * speed
```

For each surviving mutant, document it in a comment in `test_route_calculator.py`:

```python
# SURVIVING MUTANT #7
# Mutation   : distance / speed → distance * speed
# Why it survived : no test checks the numeric value of travel_time
# Fix         : assert calculate_travel_time(288, 120) == pytest.approx(2.4)
```

---

### 🎯 Step 7 — Kill the Survivors

Add targeted tests until you reach a mutation score **≥ 85 %**. After adding tests, retest only the surviving mutants (much faster than a full run):

```bash
mutmut retest
mutmut results
```

Repeat until you hit the target.

---

### 📊 Step 8 — Compare Coverage vs. Mutation Score

Run pytest with coverage on your **final** test suite:

```bash
pytest --cov=route_calculator --cov-report=term-missing -q
```

Fill in this comparison table as a comment at the top of `test_route_calculator.py`:

```python
# COMPARISON
# Line coverage  : __ %
# Mutation score : __ %
#
# Lines that are covered but mutants still survived:
#   - <function name> line <N>: <reason>
#
# Conclusion: ...
```

---

### 🤔 Step 9 — Reflect

Answer the following questions in a `# REFLECTION` section at the bottom of `test_route_calculator.py`:

1. What is the key difference between 100 % line coverage and 100 % mutation score?
2. Give one concrete example from this lab where a line was covered but the mutant still survived.
3. Why might a project choose a mutation score threshold (e.g. 80 %) for CI rather than a coverage threshold?
4. What types of mutations were hardest to kill, and why?

---

## 📦 Deliverable

1. `route_calculator.py` — unchanged bug-free version
2. `setup.cfg` — mutmut configuration
3. `test_route_calculator.py` — baseline tests + targeted tests reaching ≥ 85 % mutation score, surviving mutant comment blocks, comparison table, and reflection section
4. Final mutation score ≥ 85 % confirmed with `mutmut results`

---

> 🏗️ *FT-01 let random inputs find bugs in the code. FT-02 let deliberate code changes find gaps in your tests. In FT-03 you combine both angles: structured fuzzing that targets specific functions and reaches bugs that raw-byte fuzzing misses entirely.*
