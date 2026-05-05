# 🧪 Lab FT-03 — Structured Fuzzing with FuzzedDataProvider

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Structured Fuzzing · FuzzedDataProvider · Corpus · Dictionary &nbsp;|&nbsp; 📐 Artifacts: `route_calculator.py` · `harness_parse.py` · `harness_find_route.py` · `harness_pipeline.py` · `cities.dict` · `corpus/`

---

## 📖 Context

In FT-01 you decoded raw bytes into a string and fed it directly to `get_route_summary`. This works, but it is **inefficient for structured inputs**: the fuzzer must randomly discover that `":"` is a separator, stumble onto valid city names character by character, and waste most of its budget on inputs that fail format validation before reaching any real logic.

**`FuzzedDataProvider`** solves this by letting you extract typed, structured values from the raw fuzz bytes. You define the structure; Atheris mutates the *values* within it. The result: every fuzz iteration exercises real business logic instead of format checking.

In this lab you write **three targeted harnesses** — one per function — each progressively more structured, and compare how quickly they find bugs versus the raw approach from FT-01.

> **Note:** Atheris requires a **Linux** environment or **WSL2**.

---

## 📦 Setup

```bash
pip install atheris
```

---

## 📁 Project Structure

```
ft-03/
├── route_calculator.py
├── harness_parse.py
├── harness_find_route.py
├── harness_pipeline.py
├── cities.dict
└── corpus/
    ├── seed1
    └── seed2
```

---

## ✅ Your Tasks

### 📁 Step 1 — Create the Application Under Test

This version of the route calculator contains **3 distinct bugs** that raw-byte fuzzing struggles to reach because they only trigger on structurally valid inputs with specific value combinations. **Do not fix any bugs yet.**

```python
# route_calculator.py

LOCATIONS = {
    "Berlin":    {"Hamburg": 288, "Munich": 585, "Frankfurt": 545},
    "Hamburg":   {"Berlin": 288, "Frankfurt": 490},
    "Munich":    {"Berlin": 585, "Frankfurt": 390, "Stuttgart": 220},
    "Frankfurt": {"Berlin": 545, "Hamburg": 490, "Munich": 390, "Stuttgart": 200},
    "Stuttgart": {"Munich": 220, "Frankfurt": 200},
}

CITY_NAMES = list(LOCATIONS.keys())


def parse_route_request(request: str):
    parts = request.split(":")
    if len(parts) != 3:
        raise ValueError(f"Expected 3 colon-separated fields, got {len(parts)}")
    origin      = parts[0].strip()
    destination = parts[1].strip()
    try:
        speed = int(parts[2].strip())
    except ValueError:
        raise ValueError(f"Speed must be an integer, got: '{parts[2].strip()}'")
    if speed < 0:                          # BUG: should be <= 0
        raise ValueError("Speed must be positive")
    return origin, destination, speed


def get_distance(origin: str, destination: str) -> int:
    if origin not in LOCATIONS:
        raise ValueError(f"Unknown city: '{origin}'")
    neighbors = LOCATIONS[origin]
    if destination not in neighbors:
        raise ValueError(f"No direct link from '{origin}' to '{destination}'")
    return neighbors[destination]


def calculate_travel_time(distance: int, speed: int) -> float:
    return distance / speed              # BUG: no guard against speed == 0


def find_route(origin: str, destination: str) -> list:
    if origin not in LOCATIONS or destination not in LOCATIONS:
        raise ValueError(f"Unknown city: '{origin}' or '{destination}'")
    if origin == destination:
        return [origin]

    visited = set()
    queue   = [(origin, [origin])]

    while queue:
        current, path = queue.pop(0)
        if current in visited:           # BUG: visited check before destination check
            continue
        visited.add(current)
        for neighbor in LOCATIONS.get(current, {}):
            if neighbor not in visited:
                if neighbor == destination:
                    return path + [neighbor]
                queue.append((neighbor, path + [neighbor]))

    return []


def get_route_summary(request: str) -> str:
    origin, destination, speed = parse_route_request(request)
    route = find_route(origin, destination)

    if not route:
        raise ValueError(f"No route from '{origin}' to '{destination}'")

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

### 🌱 Step 2 — Create the Seed Corpus

A corpus gives the fuzzer valid starting points to mutate from. Without seeds Atheris starts from a single zero byte; with seeds it already knows your format.

```bash
mkdir corpus
echo -n "Berlin:Munich:120"      > corpus/seed1
echo -n "Hamburg:Frankfurt:90"   > corpus/seed2
echo -n "Stuttgart:Berlin:100"   > corpus/seed3
echo -n "Frankfurt:Stuttgart:80" > corpus/seed4
```

---

### 📖 Step 3 — Create the Dictionary File

A dictionary file tells libFuzzer which byte sequences are meaningful tokens. Atheris passes this to libFuzzer at runtime.

Create `cities.dict`:

```
# cities.dict — valid tokens for the route calculator
"Berlin"
"Hamburg"
"Munich"
"Frankfurt"
"Stuttgart"
":"
"0"
"120"
"-1"
```

---

### 🧪 Step 4 — Write `harness_parse.py`

Target: `parse_route_request`. This function takes a plain string, so raw-byte fuzzing is sufficient here — no `FuzzedDataProvider` needed.

```python
# harness_parse.py

import atheris
import sys
from route_calculator import parse_route_request


def TestOneInput(data: bytes) -> None:
    # Convert raw fuzz bytes to a string.
    # errors="replace" ensures the harness never crashes on invalid UTF-8 —
    # we want bugs in the application to surface, not in this glue code.
    text = data.decode("utf-8", errors="replace")

    try:
        # Target: parse_route_request only.
        # Fuzzing a single function is faster and produces clearer crash reports
        # than fuzzing the whole pipeline, because Atheris can explore the
        # parsing logic in isolation without routing or distance code in the way.
        parse_route_request(text)

    except ValueError:
        # ValueError means the input was structurally invalid (wrong number of
        # segments, non-integer speed, etc.).  This is expected — suppress it
        # so the fuzzer continues hunting for unhandled exceptions.
        pass

    # IndexError surfaces when split(":") returns fewer than 3 parts and the
    # code accesses parts[1] or parts[2] without checking.
    # That is a real bug — let it propagate so Atheris records the crash.


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
```

Run it:

```bash
python harness_parse.py corpus/
```

**What to look for:** Does it crash on any speed value that passes the `ValueError` check but still causes a problem downstream?

---

### 🧪 Step 5 — Write `harness_find_route.py`

Target: `find_route`. Use `FuzzedDataProvider` so the fuzzer always passes valid-looking city names — skipping format validation entirely and spending its budget on routing logic.

```python
# harness_find_route.py

import atheris
import sys
from route_calculator import find_route, CITY_NAMES


def TestOneInput(data: bytes) -> None:
    # Guard: FuzzedDataProvider raises RuntimeError on fewer than 2 bytes.
    # Returning early discards this input and lets Atheris generate a new one.
    if len(data) < 2:
        return

    # Wrap the raw bytes in a FuzzedDataProvider.
    # Instead of decoding bytes as a string, FuzzedDataProvider lets us extract
    # typed values (ints, strings, list picks) in a reproducible way.
    # Atheris mutates the underlying bytes; the provider handles the mapping.
    fdp = atheris.FuzzedDataProvider(data)

    # Always pick a valid city name from the known list.
    # This skips the ValueError("Unknown city") path entirely and forces Atheris
    # to spend its budget exploring the routing and distance logic instead.
    origin      = fdp.PickValueInList(CITY_NAMES)
    destination = fdp.PickValueInList(CITY_NAMES)

    try:
        # Target: find_route only, with structurally valid inputs.
        # We are looking for logic bugs in the BFS algorithm, not input parsing.
        find_route(origin, destination)

    except ValueError:
        # find_route raises ValueError for unknown cities — already prevented
        # above, but defensive handling keeps the harness robust.
        pass

    # Any other exception (e.g. an infinite loop that hits a recursion limit,
    # or an unexpected AttributeError) is a real bug — let it propagate.


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
```

Run it:

```bash
python harness_find_route.py corpus/
```

**What to look for:** Does the result always contain both origin and destination? Does it ever return an empty list when a path clearly exists?

> 💡 **Key FuzzedDataProvider methods:**
>
> | Method | Returns |
> |---|---|
> | `fdp.ConsumeInt(num_bytes)` | `int` |
> | `fdp.ConsumeString(max_len, "utf-8")` | `str` |
> | `fdp.PickValueInList(lst)` | element from list |
> | `fdp.ConsumeIntInRange(lo, hi)` | bounded `int` |
>
> Always guard against `len(data) == 0` — `FuzzedDataProvider` raises on empty input.

---

### 🧪 Step 6 — Write `harness_pipeline.py`

Target: the full `get_route_summary` pipeline. Use `FuzzedDataProvider` with valid cities from the list and a fuzzer-controlled speed value.

```python
# harness_pipeline.py

import atheris
import sys
from route_calculator import get_route_summary, CITY_NAMES


def TestOneInput(data: bytes) -> None:
    # Guard: we need enough bytes for two list picks and an integer.
    # 4 bytes is a safe minimum; returning early is cheaper than crashing.
    if len(data) < 4:
        return

    # Wrap the raw bytes so we can extract structured values from them.
    fdp = atheris.FuzzedDataProvider(data)

    # Always use valid city names — the fuzzer should explore the pipeline
    # logic, not waste iterations on "Unknown city" validation errors.
    origin      = fdp.PickValueInList(CITY_NAMES)
    destination = fdp.PickValueInList(CITY_NAMES)

    # ConsumeInt(4) reads 4 bytes and interprets them as a signed integer.
    # This gives the fuzzer the full integer range, including 0 and negatives —
    # exactly the values most likely to expose division-by-zero and boundary bugs.
    speed = fdp.ConsumeInt(4)

    # Reconstruct the string format that get_route_summary expects.
    # The fuzzer mutates the underlying bytes; we translate them into a
    # well-formed request so the pipeline is always reached.
    request = f"{origin}:{destination}:{speed}"

    try:
        # Exercise the entire pipeline in one call:
        # parse → find_route → get_distance → calculate_travel_time
        get_route_summary(request)

    except ValueError:
        # ValueError is raised for legitimate application errors:
        # speed <= 0 caught by a guard, no route found, etc.
        # Suppress it so the fuzzer keeps running.
        pass

    # ZeroDivisionError, KeyError, IndexError, and any other unexpected
    # exception are real bugs.  By NOT catching them, we let them surface
    # to Atheris, which saves the exact request string as a crash artifact.


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
```

Run it with the dictionary:

```bash
python harness_pipeline.py -dict=cities.dict corpus/
```

**What to look for:** Which exception type surfaces first? What input triggered it?

---

### 📊 Step 7 — Compare Raw vs. Structured Fuzzing

Re-run the FT-01 raw harness against this `route_calculator.py` for exactly 60 seconds, then run `harness_pipeline.py` for the same 60 seconds. Record the results:

| Metric | Raw (FT-01 style) | Structured (FT-03) |
|---|---|---|
| Total executions | | |
| New coverage events (`NEW` lines) | | |
| Crashes found | | |
| Time to first crash | | |

Fill in the table as a comment block at the top of `harness_pipeline.py`.

> 💡 **Tip:** Atheris prints `exec/s` on each status line. Count `NEW` log entries to estimate coverage growth.

---

### 🔬 Step 8 — Reproduce and Document Each Crash

Atheris saves crashing inputs to `crash-<hash>` files. For each crash:

```bash
python harness_pipeline.py crash-<hash>
```

Document all **3 bugs** in a `# CRASHES` comment block in `harness_pipeline.py`:

```python
# CRASH #1
# Harness that found it : harness_pipeline.py
# Crashing input        : "Berlin:Frankfurt:0"
# Exception type        : ZeroDivisionError
# Root cause (file:line): route_calculator.py:44 — calculate_travel_time
# Fix                   : guard if speed <= 0: raise ValueError(...)
#
# CRASH #2
# ...
#
# CRASH #3
# ...
```

---

### 🤔 Step 9 — Reflect

Answer these questions in a `# REFLECTION` comment at the bottom of `harness_pipeline.py`:

1. Which harness found bugs fastest, and why does targeting a lower-level function help?
2. How does the dictionary file change the mutation strategy? What would happen without it?
3. `PickValueInList` always picks a valid city name — what class of bugs does this prevent the fuzzer from finding? Is that a problem?
4. When would you combine structured fuzzing with raw-byte fuzzing in the same harness?

---

## 📦 Deliverable

1. `route_calculator.py` — unchanged buggy version
2. `cities.dict` — dictionary file with valid tokens
3. `corpus/` — at least 3 seed files
4. `harness_parse.py`, `harness_find_route.py`, `harness_pipeline.py` — all three harnesses completed
5. `harness_pipeline.py` — raw vs. structured comparison table, crash documentation for all 3 bugs, and reflection section

---

> 🏗️ *You have now worked through the full testing spectrum of this workshop: unit tests verify what you think, mutation testing measures how well they do it, raw fuzzing finds what you missed, and structured fuzzing reaches what raw fuzzing cannot. Each technique covers a blind spot the others leave open.*
