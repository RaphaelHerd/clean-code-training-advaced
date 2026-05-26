# ✅ Lab FT-01 — Solution: Fuzz Testing with Google Atheris

> 🗂️ Topic: Fuzz Testing · Coverage-Guided Fuzzing · Crash Analysis &nbsp;|&nbsp; 📐 Artifacts: `route_calculator.py` · `fuzz_harness.py` · `fuzz_findings.log` &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 🔬 Expected Findings

| Input | Exception | Root cause | Fix idea |
|---|---|---|---|
| `""` | `IndexError` | `parse_route_request` reads `parts[1]` when the destination field is missing. | Validate the request has exactly 3 fields before indexing. |
| `"Berlin:Munich"` | `IndexError` | `parse_route_request` reads `parts[2]` when the speed field is missing. | Reject missing speed with a controlled `ValueError`. |
| `"Berlin:Munich:0"` | `ZeroDivisionError` | `calculate_travel_time` divides by zero speed. | Validate `speed > 0` before calculating travel time. |

Representative base64 values for reproduction:

| Input | Base64 |
|---|---|
| `""` | empty string |
| `"Berlin:Munich"` | `QmVybGluOk11bmljaA==` |
| `"Berlin:Munich:0"` | `QmVybGluOk11bmljaDow` |

---

## 🤔 Step 7 — Reflection

1. **What kinds of bugs did the fuzzer find that a typical unit test would likely miss?**

   It found malformed input and boundary-value bugs: empty input, missing route fields, and zero speed. These are common parser-edge cases that are easy to miss when tests focus on valid examples.

2. **How does Atheris use coverage feedback to guide input mutation?**

   Atheris keeps inputs that reach new branches or code paths, then mutates those inputs further. A valid seed such as `Berlin:Munich:120` helps it reach deeper parsing and travel-time logic quickly.

3. **When would you prefer fuzzing over property-based testing?**

   Use fuzzing when the input space is broad, parser-like, byte-oriented, or poorly understood, and the main goal is discovering crashes. Use property-based testing when expected invariants can be stated clearly.

4. **What are the limitations of this fuzzing approach for this application?**

   The harness mainly detects uncaught exceptions. It does not prove that distances, routes, or travel times are semantically correct unless additional assertions or domain oracles are added.

---

## 💡 Trainer Notes

- The empty-input crash is usually found immediately because libFuzzer tries `""` before mutating the corpus.
- A seed corpus makes the zero-speed bug much easier to reach because Atheris starts from valid `ORIGIN:DESTINATION:SPEED` shapes.
- `ValueError` is suppressed in the harness because unknown cities and non-numeric speeds are treated as controlled application failures for this exercise.
