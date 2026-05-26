# ✅ Lab UT-07 — Solution: Dynamic Fakes with pytest-mock

> 🗂️ Topic: Isolation Frameworks · pytest-mock · MagicMock · patch &nbsp;|&nbsp; 📐 Artifacts: Comparison answers &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 📊 Step 5 — Compare Handwritten vs. Dynamic Fakes

| Property | Handwritten | MagicMock |
|---|---|---|
| **Lines of code per fake** | More code. Each fake class, field, method, and recorded value must be written manually. | Very little code. Usually one `MagicMock()` plus optional `return_value`, `side_effect`, or assertions. |
| **Explicit about interface?** | Yes. The fake shows exactly which methods the test double supports. | No by default. A plain `MagicMock` accepts almost any method or attribute name. |
| **Catches typos in methods?** | Yes, usually. Calling a method the handwritten fake does not implement raises `AttributeError`. | No by default. Misspelled method names create new mocks silently unless `spec` or `autospec` is used. |
| **Configurable return values** | Yes, but you must add fields or constructor arguments yourself. | Yes. Use `return_value` for fixed results. |
| **Can simulate exceptions?** | Yes, but you must write the raising behavior yourself. | Yes. Use `side_effect` to raise an exception. |

---

## 💡 Trainer Notes

- Handwritten fakes are more verbose, but they make the fake's contract visible.
- `MagicMock` is fast to write and records calls automatically, which is useful for interaction tests.
- A plain `MagicMock` is intentionally permissive. Use stricter mocks later when method-name mistakes should fail immediately.
