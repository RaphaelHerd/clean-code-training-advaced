# ✅ Lab UT-04 — Solution: Injection Techniques

> 🗂️ Topic: Constructor Injection · Property Injection · Dependency Injection &nbsp;|&nbsp; 📐 Artifacts: Comparison answers &nbsp;|&nbsp; 🔒 Trainer Reference

---

## 🤔 Step 6 — Compare the Two Techniques

| Question | Answer |
|---|---|
| **1. Why is `manager` injected via the constructor but `logger` via a property?** | `manager` is required for the core behavior of `LogAnalyzer`. Without an `ExtensionManager`, the analyzer cannot decide whether a file extension is valid, so the dependency should be explicit at construction time. `logger` is optional support behavior. The analyzer can still do its main job without a custom logger because `NullLogger` provides a safe default, so property injection lets tests and callers override it only when they care about logging. |
| **2. What would break if you made `manager` optional with a default `FileExtensionManager`?** | The explicit constructor contract would break: `LogAnalyzer()` would no longer raise `TypeError`, so `test_constructor_requires_manager` would fail. More importantly, unit tests could silently fall back to the real `FileExtensionManager`, which reads `extensions.txt`. That makes tests depend on the filesystem and the current working directory, turning a simple unit test into an accidental integration test. It also hides the fact that extension validation is mandatory behavior. |
| **3. When would you choose property injection even for a required dependency?** | Only when construction cannot receive the dependency directly, usually because a framework creates the object first and wires dependencies later. Examples include serializers, ORMs, UI frameworks, plugin loaders, or legacy containers that require a parameterless constructor. In that case the class should still fail fast before use if the property was not set, or a factory/builder should guarantee the required property is assigned. |

---

## 💡 Trainer Notes

- Constructor injection is the default choice for required collaborators because it makes invalid object construction impossible.
- Property injection fits optional collaborators when there is a harmless default, such as `NullLogger`.
- Property injection for required dependencies is a compromise for framework or lifecycle constraints, not the normal design choice.
