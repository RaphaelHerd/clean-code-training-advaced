# ✅ Lab DDD-01 — Solution: Modelling ClinicCare with Domain-Driven Design

> 🗂️ Topic: DDD · Bounded Contexts · Aggregates · Value Objects · Domain Events &nbsp;|&nbsp; 📐 Artifacts: `clinicare/` package · `tests/` · Context Map &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 🗺️ Step 2 — Bounded Contexts

| Bounded Context | Owns | Produces | Consumes |
|---|---|---|---|
| **Patient Management** | Patient identity, name, date of birth | `PatientRegistered`, `PatientUpdated` | None |
| **Treatment** | Case identity, case status, medication orders | `CaseOpened`, `MedicationPrescribed`, `CaseClosed` | `PatientRegistered`, `PatientUpdated` |
| **Reporting** | Monthly counters only | None | `PatientRegistered`, `CaseOpened`, `MedicationPrescribed` |

---

## 🚀 Step 8 — Run the Solution

Run from `solution/ddd-01/src`:

```bash
python -m clinicare.cli.demo
```

---

## 💡 Trainer Notes

- The main learning point is the location of business rules: invariants live in aggregates, not in controllers or repositories.
- The application layer owns orchestration order. Persist first, publish after.
- Reporting is deliberately a projection, not another aggregate.
- The event payloads are intentionally small. Events crossing context boundaries should not leak private patient data.
