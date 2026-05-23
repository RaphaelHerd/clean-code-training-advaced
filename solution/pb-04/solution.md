# ✅ Lab PB-04 — Solution: Basket Invariants

> 🗂️ Topic: Property-Based Testing · Custom Strategies · `@composite` · Domain Invariants &nbsp;|&nbsp; 📐 Artifacts: `basket.py` · `test_basket.py` &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 🤔 Step 6 — Reflection

1. **Which invariant would be hardest to find with example-based tests alone, and why?**

   The `total()` bug for baskets with more than 5 items is a good candidate. Example-based tests often use one or two items, so they can easily miss a size-dependent branch that only appears at 6 items.

2. **What does `assume()` do, and what is the risk of overusing it?**

   `assume()` discards generated examples that do not satisfy a precondition. It is useful when a property only applies to a subset of inputs. The risk is filtering out too many examples, which makes Hypothesis slower and can trigger health-check warnings.

3. **Why did Hypothesis shrink the failing basket to exactly 6 items in Step 5?**

   The bug only appears when `len(self._items) > 5`. Hypothesis tries to simplify failing examples while keeping the failure. A 6-item basket is the smallest basket that still enters the broken branch.

---

## 💡 Trainer Notes

- Encourage students to keep the strategy realistic. A custom strategy that generates impossible domain states can create misleading failures.
- `assume(name not in basket.item_names())` is not just a Hypothesis detail; it expresses the precondition under which the removal invariant is true.
