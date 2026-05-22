# ✅ Lab FT-03 — Solution: Structured Fuzzing with FuzzedDataProvider

> 🗂️ Topic: Structured Fuzzing · FuzzedDataProvider · Corpus · Dictionary &nbsp;|&nbsp; 📐 Artifacts: `route_calculator.py` · `harness_parse.py` · `harness_find_route.py` · `harness_pipeline.py` · `cities.dict` · `corpus/` &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 🔬 Expected Findings

FT-03 shows why structured fuzzing is useful:

> Instead of hoping that random bytes become a valid route request, the harness maps bytes into meaningful values such as city names and speeds.

The application expects requests shaped like this:

```text
ORIGIN:DESTINATION:SPEED
```

The three harnesses target three different levels of the route calculator:

| Harness | Expected finding |
|---|---|
| `harness_parse.py` | `IndexError` when the request is missing fields. |
| `harness_find_route.py` | Timeout / infinite loop in `find_route` for some valid city pairs. |
| `harness_pipeline.py` | `ZeroDivisionError` when structured input creates `speed == 0`. It may also hit the route timeout first. |

Representative reproductions:

| Harness | Example input | Result |
|---|---|---|
| `harness_parse.py` | `""` or `"Berlin"` | `IndexError` |
| `harness_find_route.py` | a multi-hop city pair such as `Berlin` → `Stuttgart` | libFuzzer timeout |
| `harness_pipeline.py` | bytes that build a request such as `"Berlin:Berlin:0"` | `ZeroDivisionError` |
| `harness_pipeline.py` | bytes that build a multi-hop route | possible libFuzzer timeout in `find_route` |

---

## 🧪 What Each Harness Teaches

### `harness_parse.py`

This harness targets only `parse_route_request`.

The parser indexes split fields before checking whether they exist:

```python
parts = request.split(":")
origin      = parts[0].strip()
destination = parts[1].strip()
speed       = int(parts[2].strip())
```

Requests such as `""` or `"Berlin"` therefore raise `IndexError`. The harness catches `ValueError`, because that represents controlled application validation, but it lets `IndexError` escape so Atheris records the real parser crash.

Fix idea:

```python
if len(parts) != 3:
    raise ValueError("Request must use ORIGIN:DESTINATION:SPEED")
```

Malformed input should be rejected deliberately, not fail with an accidental list-indexing error.

---

### `harness_find_route.py`

This harness targets only `find_route` and uses structured city values:

```python
origin = fdp.PickValueInList(CITY_NAMES)
destination = fdp.PickValueInList(CITY_NAMES)
```

That skips parser and unknown-city noise. The fuzzer spends its time inside the route-search algorithm.

The bug is subtle:

```python
while queue:
    current, path = queue[0]         # BUG: this only looks at the first item
    if current in visited:
        continue
```

`queue[0]` only reads the first item. It does not remove it. After the first iteration, the same city remains at the front of the queue, but it is now in `visited`. The next iteration hits `continue`, jumps back to the top, reads the same queue item again, and loops forever.

For `origin == destination`, the function returns before the loop, so not every input hangs. Structured fuzzing helps because it quickly tries many valid city pairs until one reaches the broken loop.

Fix idea:

```python
current, path = queue.pop(0)
```

Run this harness with a short timeout:

```bash
python harness_find_route.py -timeout=2 corpus/
```

---

### `harness_pipeline.py`

This harness targets the full workflow:

```text
parse → find_route → get_distance → calculate_travel_time
```

It builds valid-looking requests from structured values:

- valid origin city
- valid destination city
- fuzzer-controlled integer speed

The parser accepts speed `0` because it only rejects negative speeds:

```python
if speed < 0:
```

Later, travel time is calculated with:

```python
return distance / speed
```

When `speed == 0`, this raises `ZeroDivisionError`.

The pipeline may also hit the route timeout before it reaches the division. To isolate the speed bug, use a same-city route such as `"Berlin:Berlin:0"` so `find_route` returns immediately.

Fix idea: reject `speed <= 0`, ideally in `parse_route_request`, and keep `calculate_travel_time` defensive as well.

---

## 📊 Raw vs. Structured Fuzzing

| Question | Raw FT-01-style harness | Structured FT-03 harness |
|---|---|---|
| What does the fuzzer mutate? | Arbitrary bytes decoded as text. | Bytes mapped into cities and integers. |
| How often does it reach route logic? | Rarely, unless it discovers valid city names and separators. | Very often, because the harness chooses valid cities. |
| What does the dictionary help with? | It gives raw mutation useful tokens like city names, `:`, `0`, and `-1`. | It still helps libFuzzer mutate toward meaningful values. |
| Why does `speed == 0` appear quickly? | Only after a valid request shape is discovered. | The harness always creates a valid request shape and lets speed vary. |

Structured fuzzing is more focused. Atheris still mutates bytes, but the harness translates those bytes into values that reach the code path we care about.

---

## 🤔 Step 9 — Reflection

1. **Which harness found bugs fastest, and why does targeting a lower-level function help?**

   `harness_parse.py` can find the missing-field parser crash quickly because it calls only the parser. `harness_find_route.py` can find the route timeout quickly because it always passes valid cities. `harness_pipeline.py` reaches deep workflow bugs because it always builds a request in the right shape.

   Targeting a lower-level function removes unrelated setup. The fuzzer spends more time on the behaviour under test and less time getting through earlier validation.

2. **How does the dictionary file change the mutation strategy? What would happen without it?**

   The dictionary gives libFuzzer useful tokens such as city names, `:`, `0`, and `-1`. Without it, the fuzzer must discover useful strings byte by byte. With it, mutations are much more likely to stay close to meaningful route requests.

3. **`PickValueInList` always picks a valid city name — what class of bugs does this prevent the fuzzer from finding? Is that a problem?**

   It prevents this harness from testing unknown-city handling. That is intentional here because the route and pipeline harnesses are trying to reach deeper logic. It would be a problem only if unknown-city validation were the target. In that case, write a separate harness that sometimes generates invalid city names.

4. **When would you combine structured fuzzing with raw-byte fuzzing in the same harness?**

   Combine them when both syntax and deeper business logic matter. For example, use raw bytes to test the parser, then structured values to test route search, pricing, or calculations after parsing succeeds.

---

## 💡 Trainer Notes

- Keep `route_calculator.py` buggy in the lab. Students should discover the failures by fuzzing first.
- `harness_parse.py` demonstrates parser robustness: missing fields should produce controlled errors.
- `harness_find_route.py` demonstrates timeout detection and why consuming work queues correctly matters.
- `harness_pipeline.py` demonstrates why boundary values such as `0` matter in full workflows.
- Run the route harness with a short timeout such as `-timeout=2`, otherwise an infinite loop can look like a stuck terminal session.
