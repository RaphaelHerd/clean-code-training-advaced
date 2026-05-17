# ✅ Lab UT-05 — Solution: Handwritten Mock Objects

> 🗂️ Topic: Interaction Testing · Mock Objects · Stub vs. Mock &nbsp;|&nbsp; 📐 Artifacts: Comparison answers &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 🤔 Step 5 — Stub vs. Mock: Know the Difference

| Property | Stub | Mock |
|---|---|---|
| **Purpose** | Provides controlled indirect input so the unit under test can run without real dependencies. | Records and verifies outgoing calls made by the unit under test. |
| **Can fail a test?** | No. A stub only supplies behavior or data; the test's assertions fail, not the stub itself. | Yes. A mock can fail the test when an expected call, argument, or call count is missing or wrong. |
| **Checks return values?** | Yes, indirectly. Stubs help test return values or state by controlling what dependencies return. | Usually no. Mocks focus on interactions, not returned state. |
| **Checks outgoing calls?** | No. A plain stub does not prove that a collaborator was called. | Yes. That is the main reason to use a mock. |
| **Recommended per test** | As many as needed to isolate the unit and set up inputs. | No more than one mock per test; split the test if several interactions need verification. |

---

## 💡 Trainer Notes

- A stub helps answer: "Given this dependency behavior, what does my unit return or change?"
- A mock helps answer: "Did my unit call the right collaborator in the right way?"
- Use mocks only for behavior that has no better observable result, such as notifying `WebService` about an invalid filename.
