# ✅ Lab FT-02 — Solution: Mutation Testing with mutmut

> 🗂️ Topic: Mutation Testing · Test Quality · Mutation Score · Coverage vs. Mutation &nbsp;|&nbsp; 📐 Artifacts: `route_calculator.py` · `test_route_calculator.py` · `setup.cfg` &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 🎯 Expected Results

| Check | Expected result |
|---|---|
| `python -m pytest -q` | `25 passed` |
| `python -m pytest --cov=route_calculator --cov-report=term-missing -q` | `96 %` line coverage |
| `mutmut run && mutmut results` | approximately `73/77` killed, `94.81 %` mutation score |

The exact number of mutants can vary slightly by Python and mutmut version. The important result is that the final mutation score is above the lab target of `85 %`.

This solution keeps the application code unchanged and improves only the tests. The test suite checks normal routes, invalid input, important boundary values, and exact summary output.

---

## 🔬 What Mutation Testing Revealed

Mutation testing asks: “If this line of production code were changed by accident, would the tests notice?”

The first version of a test suite often executes the code but does not assert enough detail. The following table shows the kind of weakness mutmut exposes and how the final tests close that gap:

| Test weakness | Why it matters | Test that covers it |
|---|---|---|
| The parser rejected invalid speeds, but did not prove that `1` is valid. | A mutant changed `speed <= 0` to `speed <= 1`. That would reject the smallest valid positive speed. | `test_parse_accepts_minimum_positive_speed` |
| Travel-time calculation was tested with a normal speed, but not with the lower valid boundary. | Boundary values are where comparison mutants often survive. | `test_calculate_travel_time_accepts_speed_one` |
| The speed error test used a loose message check. | A changed error message could still pass if it contained the same substring. | `test_calculate_travel_time_rejects_non_positive_speed` |
| The route summary was initially checked only for city names. | A summary could contain the right cities but the wrong distance, route order, time, or formatting. | `test_get_route_summary_contains_distance_and_time`, `test_get_route_summary_multi_hop`, `test_get_route_summary_same_city` |

Representative killed mutants:

| Mutant | Mutation | Why the final tests catch it |
|---|---|---|
| `route_calculator.x_parse_route_request__mutmut_15` | `speed <= 0` → `speed <= 1` | The parser test proves that `Berlin:Munich:1` is valid. |
| `route_calculator.x_calculate_travel_time__mutmut_2` | `speed <= 0` → `speed <= 1` | The travel-time test proves that distance divided by speed `1` works. |
| `route_calculator.x_calculate_travel_time__mutmut_4` | `"Speed must be positive"` → `"XXSpeed must be positiveXX"` | The error test checks the exact exception message. |

---

## 🧟 Representative Survivors

Some mutants can survive even when the tests are useful. A survivor means “the tests did not observe a behaviour change,” not automatically “the tests are bad.”

| Mutant | Mutation | Why it survived |
|---|---|---|
| `route_calculator.x_find_route__mutmut_14` | `visited.add(current)` → `visited.add(None)` | In this small connected graph, the destination is still eventually found. |
| `route_calculator.x_find_route__mutmut_16` | `LOCATIONS.get(current, {})` → `LOCATIONS.get(current, None)` | Every queued city is a known city, so the default value is never used. |
| `route_calculator.x_find_route__mutmut_18` | `LOCATIONS.get(current, {})` → `LOCATIONS.get(current)` | For known cities, both expressions return the same neighbours. |

These survivors are good examples for discussion: mutation testing points to possible gaps, but humans still decide whether a surviving mutant represents a meaningful requirement.

---

## 📊 Coverage vs. Mutation Score

| Metric | Result |
|---|---|
| Line coverage | `96 %` |
| Mutation score | approximately `94.81 %` |

Coverage and mutation score answer different questions:

| Metric | Question it answers |
|---|---|
| Line coverage | “Did the tests run this line?” |
| Mutation score | “Would the tests fail if this logic changed?” |

Covered lines with surviving mutants:

| Function | Line | What this teaches |
|---|---:|---|
| `find_route` | 55 | Running a line is not enough; the test must also observe a behaviour that changes when the line is wrong. |
| `find_route` | 56 | A changed default value can be invisible when all normal inputs use known cities. |

Conclusion: coverage is useful, but it can be too optimistic. Mutation testing is stricter because it checks whether the tests would catch real changes in behaviour.

---

## 🤔 Step 9 — Reflection

1. **What is the key difference between 100 % line coverage and 100 % mutation score?**

   Line coverage means every line was executed. Mutation score means the tests were strong enough to detect deliberate changes to the code. A test can execute a line and still miss a bug if it does not assert the important outcome.

2. **Give one concrete example from this lab where a line was covered but the mutant still survived.**

   The route-search loop was covered by direct and multi-hop route tests, but changing `visited.add(current)` to `visited.add(None)` still survived. For this small graph, the route is still found, so the public result does not change.

3. **Why might a project choose a mutation score threshold for CI rather than a coverage threshold?**

   A mutation threshold encourages tests that catch regressions. A coverage threshold can be satisfied by shallow tests that call the code without checking exact values, boundaries, or error behaviour.

4. **What types of mutations were hardest to kill, and why?**

   The hardest mutations were near-equivalent changes in `find_route`. The graph is small and all real cities are connected, so some internal changes do not affect the visible route results for normal inputs.

---

## 💡 Trainer Notes

- The strongest teaching point is the difference between executing code and checking behaviour.
- Boundary tests such as `speed == 1` are small, but they kill important comparison mutants.
- Exact assertions are valuable when formatting or error messages are part of the expected behaviour.
- Surviving mutants should be reviewed, not blindly chased. Some survivors are equivalent for the current domain model.
