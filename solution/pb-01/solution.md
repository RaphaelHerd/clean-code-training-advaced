# ✅ Lab PB-01 — Solution: From Examples to Properties

> 🗂️ Topic: Property-Based Testing · Hypothesis · `@given` · Strategies &nbsp;|&nbsp; 📐 Artifacts: `calculator.py` · `test_calculator.py` &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 📊 Example-Based vs. Property-Based

| Question | Example-Based | Property-Based |
|---|---|---|
| Who chooses the inputs? | The test author chooses each case manually. | Hypothesis generates many cases from a strategy. |
| How many cases are tested? | Usually a small fixed set. | Usually many generated cases per test. |
| Can it find unexpected bugs? | Only if the author happened to include the relevant example. | Yes, if the property describes the expected rule well. |
| What do you assert? | A specific input has a specific output. | A general rule holds for all generated inputs. |
| What happens when it fails? | The failing hand-written example is reported. | Hypothesis reports and shrinks a counterexample. |

---

## 🤔 Step 7 — Reflection

1. **What did the example tests prove?**

   They proved that `add` works for four specific input pairs. They did not prove that addition works for every integer pair.

2. **Why did the Step 3 bug survive?**

   The bug only changes behaviour when `a == 0`, and none of the four example tests uses `0` as the first argument.

3. **Why did the commutativity property catch it?**

   The property compares both argument orders. For `a=0, b=1`, the broken implementation returns different results for `add(0, 1)` and `add(1, 0)`.

4. **What is the main limitation of property-based testing?**

   The property must be meaningful. Hypothesis can generate many inputs, but it cannot know the domain rule unless the test expresses it.

---

## 💡 Trainer Notes

- `pytest -v -s` is needed in Step 6 because pytest captures output from passing tests by default.
- The exact examples printed by Hypothesis can vary by version, seed, and previous failure database state. The important observation is that it explores generated inputs and reports minimal counterexamples when a property fails.
