---
description: Implement New Game Logic
auto_execution_mode: 3
---

**Objective:** To implement and document a single, testable feature from an initiative.
**Process:**
    1. **Agent:** Generate a failing `spec-kit` test for the target feature.
    2. **Agent:** Implement the minimal code to make the test pass.
    3. **Agent:** Refactor the code for clarity and adherence to all project rules.
    4. **Agent:** Run all quality checks (`ruff`, `mypy`).
    5. **Agent:** If the feature is identified as performance-sensitive in ADR-0005, create and run a benchmark test in the `tests/benchmarks/` directory to ensure it meets the defined performance budget.
    6. **Agent:** Invoke the `[DOCS] Update Living Documentation` workflow.
    7. **Agent:** (Self-Correction) Briefly analyze the implementation. Note any potential future improvements or technical debt in a comment block (e.g., `# TECH_DEBT: This could be optimized...`).
