# 🧪 Lab FT-01 — Fuzz Testing with Google Atheris

> 👤 **Individual Exercise** &nbsp;|&nbsp; 🗂️ Topic: Fuzz Testing · Coverage-Guided Fuzzing · Crash Analysis &nbsp;|&nbsp; 📐 Artifacts: `route_calculator.py` · `fuzz_harness.py`

---

## 📖 Context

Unit tests verify the inputs you thought to test. A fuzzer verifies inputs you never would have thought of. **Google Atheris** is a coverage-guided Python fuzzer: it generates random, mutated byte sequences, feeds them to your code, and tracks which branches it hits — steering future mutations towards unexplored paths.

In this lab you receive a small **Route Calculator** that parses text-based route requests between German cities and computes travel time and distance. The developer wrote it quickly and shipped it with no tests. Your job is to fuzz it, let Atheris find the bugs, and then reason about what went wrong from the crash reports alone.

> **Note:** Atheris requires a **Linux** environment or **WSL2** (Windows Subsystem for Linux). It does not run natively on Windows or macOS ARM.

---

## ✅ Your Tasks

### 🛠️ Step 0 — Install Atheris on WSL2 Ubuntu

Atheris requires a Linux environment. Run this lab inside WSL2 with an Ubuntu distro.

**1. Launch your Ubuntu WSL2 distro** from PowerShell or Windows Terminal:

```powershell
wsl -d Ubuntu
```

**2. Update packages and install system dependencies.**
Atheris needs Python development headers, the full Python stdlib, and the Clang compiler (which bundles libFuzzer):

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-full python3-dev clang python3.12-venv
```

**3. Create a virtual environment and activate it.**
Ubuntu 22.04+ blocks global `pip` installs (PEP 668). Use a venv instead:

```bash
python3 -m venv ~/fuzz-env
source ~/fuzz-env/bin/activate
```

Your prompt will change to `(fuzz-env)`. All subsequent `python` and `pip` commands now target this environment.

**4. Install Atheris inside the venv:**

```bash
pip install atheris
```

> **Tip:** If the install fails with a compilation error, Clang may not be picked up as the default compiler. Force it explicitly:
> ```bash
> CC=clang pip install atheris
> ```

**5. Verify the installation:**

```bash
python -c "import atheris; print('Atheris OK')"
```

> **Remember:** Every time you open a new WSL2 terminal for this lab, re-activate the venv first:
> ```bash
> source ~/fuzz-env/bin/activate
> ```

---

### 📁 Step 1 — Create the Application Under Test

Create `route_calculator.py` exactly as shown. **Do not fix any bugs yet** — the fuzzer will find them for you.

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
    origin      = parts[0]
    destination = parts[1]
    speed       = int(parts[2])
    return origin, destination, speed


def get_distance(origin: str, destination: str) -> int:
    """Return the direct distance (km) between two directly connected locations."""
    return LOCATIONS[origin][destination]


def calculate_travel_time(distance: int, speed: int) -> float:
    """Return travel time in hours."""
    return distance / speed


def find_route(origin: str, destination: str) -> list:
    """BFS shortest-hop path between two locations."""
    if origin not in LOCATIONS or destination not in LOCATIONS:
        raise ValueError(f"Unknown location: '{origin}' or '{destination}'")

    visited = set()
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

### 🔍 Step 2 — Explore the Application

Run the application manually to understand what it does before fuzzing it:

```python
from route_calculator import get_route_summary
print(get_route_summary("Berlin:Munich:120"))
print(get_route_summary("Hamburg:Frankfurt:90"))
```

Note: what happens with an unknown city? A zero speed? A missing segment?

---

### 🧪 Step 3 — Write the Fuzz Harness

Create `fuzz_harness.py`. Atheris calls your `TestOneInput` function repeatedly with random mutated byte sequences. Decode the bytes and pass the result to `get_route_summary`.

```python
# fuzz_harness.py

import atheris
import sys
from route_calculator import get_route_summary


def TestOneInput(data: bytes) -> None:
    """
    Atheris calls this function repeatedly with random/mutated byte sequences.
    Our job: convert those bytes into a string and feed it to the application.
    """
    # Decode the raw fuzz bytes into a Python string.
    # errors="replace" swaps any byte sequence that is not valid UTF-8 with a
    # replacement character (U+FFFD) instead of raising UnicodeDecodeError.
    # We never want the *harness* to crash — only the *application* should crash.
    text = data.decode("utf-8", errors="replace")

    try:
        # Feed the decoded string into the full pipeline.
        # Atheris will call this function millions of times with different
        # mutations, tracking which branches are newly covered each time.
        get_route_summary(text)

    except ValueError:
        # ValueError is intentional application behaviour: unknown city, wrong
        # format, etc.  Suppressing it lets the fuzzer keep running through
        # valid error-handling paths without stopping.
        pass

    # Any other exception — IndexError, KeyError, ZeroDivisionError — is an
    # unhandled bug.  By NOT catching it, we let it propagate back to Atheris,
    # which records the exact bytes that triggered it as a crash artifact.


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
```

> 💡 **Tip:** Use `data.decode("utf-8", errors="replace")` to handle invalid byte sequences safely. A `ValueError` from `find_route` is expected application behaviour — suppress it. Any other exception (`IndexError`, `KeyError`, `ZeroDivisionError`) is a bug — do not catch it.

---

### ▶️ Step 4 — Run the Fuzzer

```bash
python fuzz_harness.py
```

Let it run for **at least 2–3 minutes**. Atheris prints a status line as it works:

```
#0      READ units: 1
#1      INITED cov: 12 ft: 12 corp: 1/1b exec/s: 0 rss: 40Mb
#64     NEW    cov: 17 ...
```

When it finds a crash it stops and saves the input:

```
SUMMARY: libFuzzer: deadly signal
artifact_prefix='./'; Test unit written to ./crash-<hash>
```

---

### 🔬 Step 5 — Reproduce and Identify Each Crash

Atheris saves each crashing input to a file named `crash-<hash>`. Reproduce it manually:

```python
crash_input = open("crash-<hash>", "rb").read()
from route_calculator import get_route_summary
get_route_summary(crash_input.decode("utf-8", errors="replace"))
```

For **each crash** you find, document it in a comment block in `fuzz_harness.py`:

```python
# CRASH #1
# Input that caused it : ...
# Exception type       : ...
# Root cause (line)    : ...
# Fix idea             : ...
```

The fuzzer should surface **at least 3 distinct crash categories**. Try to find all of them before looking at the code.

---

### 🌱 Step 6 — Warm the Fuzzer with a Corpus (Optional Bonus)

A seed corpus gives Atheris a head start — instead of discovering the colon-separated format from scratch, it begins with valid inputs and mutates their values:

```bash
mkdir corpus
echo -n "Berlin:Munich:120"    > corpus/seed1
echo -n "Hamburg:Frankfurt:90" > corpus/seed2
echo -n "Stuttgart:Berlin:100" > corpus/seed3
```

Run with the corpus:

```bash
python fuzz_harness.py corpus/
```

Observe how much faster Atheris reaches deep code paths compared to running without seeds.

---

### 🤔 Step 7 — Reflect

Answer the following questions in a `# REFLECTION` section at the bottom of `fuzz_harness.py`:

1. What kinds of bugs did the fuzzer find that a typical unit test would likely miss?
2. How does Atheris use coverage feedback to guide input mutation?
3. When would you prefer fuzzing over property-based testing?
4. What are the limitations of this fuzzing approach for this application?

---

## 📦 Deliverable

1. `route_calculator.py` — the application under test, unmodified
2. `fuzz_harness.py` — completed `TestOneInput`, crash documentation blocks for at least 3 crashes, and the reflection section
3. (Optional) `corpus/` folder with seed files

---

> 🏗️ *In FT-02 you switch perspective: instead of throwing random inputs at the code, you measure how well your own tests would catch deliberate bugs — using mutation testing with mutmut.*
