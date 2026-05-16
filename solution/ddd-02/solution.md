# ✅ Lab DDD-02 — Solution: Hexagonal Architecture for One ClinicCare Slice

> 🗂️ Topic: Hexagonal Architecture · Ports & Adapters · Domain Events · Projections &nbsp;|&nbsp; 📐 Artifacts: `clinicare_hex_min/` package · `tests/test_min.py` &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 🚀 Step 6 — Run the Solution

Run from `solution/ddd-02/src`:

```bash
python -m pytest -v
python -m clinicare_hex_min.adapters.driver.cli_demo
```

Expected CLI output:

```text
New patients this month: 2
```

---

## 💡 Trainer Notes

- The important boundary is dependency direction, not the number of folders.
- The injected `Clock` is a small but important port because it keeps the core deterministic.
- The in-memory adapters are intentionally simple. Their purpose is to prove the core can run without a database, web framework, or message broker.
- The same use case could later be driven by HTTP, a queue consumer, or a CLI without changing the core.
