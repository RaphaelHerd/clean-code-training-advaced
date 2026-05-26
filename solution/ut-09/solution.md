# ✅ Lab UT-09 — Solution: TDD: Red · Green · Refactor

> 🗂️ Topic: Test-Driven Development · Red-Green-Refactor · Incremental Design &nbsp;|&nbsp; 📐 Artifacts: Reflection answers &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 📊 Step 5 — Reflect on the TDD Process

| Question | Answer |
|---|---|
| **1. At what point did you feel forced to generalize beyond a hardcoded return value?** | The second test forced generalization. After `test_password_shorter_than_8_chars_is_invalid`, the validator could have returned `False` for everything. `test_password_of_exactly_8_chars_is_valid` forced the code to inspect the actual password length instead of returning a hardcoded result. Later cycles repeated the same pattern for uppercase and special-character rules. |
| **2. Did any test you wrote catch a regression introduced by a later cycle? Which one?** | Yes. The earlier valid-password test caught that `"abcd1234"` was no longer valid once the uppercase rule was introduced. Later, `"Abcd1234"` was no longer valid after the special-character rule. Those failures showed that the test data had to evolve with the rules, and that a truly valid example must satisfy all current validation rules. |
| **3. What is the difference between writing tests after code vs. before code in terms of the design decisions you made?** | Writing tests before code made the public API appear from the caller's point of view: `PasswordValidator().validate(password)` returning a `ValidationResult` with `is_valid` and `errors`. Each design decision was added only when a test needed it. Writing tests after code usually starts from an existing implementation, so tests tend to confirm the design instead of shaping it. |
| **4. When would you NOT use TDD? Give one concrete scenario.** | Strict TDD is usually not the right fit during exploratory work where the goal is to discover whether an approach is even possible. For example, when spiking an unfamiliar third-party password-strength library, a small throwaway prototype can help reveal its API and behavior first. TDD becomes useful again once the desired design is clear. |

---

## 💡 Trainer Notes

- TDD generalizes behavior by forcing each new test to disprove the previous simplest implementation.
- Earlier tests act as a safety net, but their test data may need to be updated when the business rules become more specific.
- The main design benefit is caller-first API pressure: production code grows in response to observable behavior, not speculation.
