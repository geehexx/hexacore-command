# Windsurf Workflows for Hexa-Core Command

## Workflow: `[INITIATIVE] Execute MVP Roadmap`

**Objective:** To autonomously complete all tasks defined in `docs/MVP_Roadmap.md`.

**Process:**

1. **Agent:** Announce you are beginning the MVP initiative.
2. **Agent:** For each task in `docs/MVP_Roadmap.md`:
  * Invoke the `[TDD] Implement New Game Logic` workflow for the task.
  * On successful completion, update the roadmap by checking off the item.
3. **CHECKPOINT: MVP Completion Review.**
  * **Presentation:** "The MVP Roadmap is complete. All core engine features have been implemented and documented."
  * **Verification:** Provide a final summary of the project state, confirming all tests pass and quality checks are clean.
  * **Action:** Propose archival of `docs/MVP_Roadmap.md` and await the next high-level directive.

## Workflow: `[TDD] Implement New Game Logic`

**Objective:** To implement and document a single, testable feature from an initiative.

**Process:**

1. **Agent:** Generate a failing `spec-kit` test for the target feature.
2. **Agent:** Implement the minimal code to make the test pass.
3. **Agent:** Refactor the code for clarity and adherence to all project rules.
4. **Agent:** Run all quality checks (`ruff`, `mypy`).
5. **Agent:** If the feature is identified as performance-sensitive in ADR-0005, create and run a benchmark test in the `tests/benchmarks/` directory to ensure it meets the defined performance budget.
6. **Agent:** Invoke the `[DOCS] Update Living Documentation` workflow.
7. **Agent:** (Self-Correction) Briefly analyze the implementation. Note any potential future improvements or technical debt in a comment block (e.g., `# TECH_DEBT: This could be optimized...`).

## Workflow: `[DOCS] Update Living Documentation`

**Objective:** To ensure all documentation reflects the current state of the code.

**Process:**

1. **Agent:** Identify which constitutional or living documents are affected by the recent code changes.
2. **Agent:** Update the relevant sections with detailed, clear explanations of the implementation.
3. **Agent:** If a change necessitates a modification to a core rule, halt and invoke the `[PLAN] Propose New ADR` workflow instead.

## Workflow: `[PLAN] Propose New ADR`

**Objective:** To formalize a significant architectural decision.

**Process:**

1. **Agent:** "I have identified a need for an architectural decision regarding [topic]."
2. **Agent:** (Asks clarifying, high-level questions to the user to understand constraints and goals).
3. **Agent:** "Based on your input, I will draft an ADR." (Generates the ADR in `docs/decisions/`).
4. **CHECKPOINT: ADR Review.**
  * **Presentation:** "The draft ADR is ready for your review. It proposes [decision] to solve [problem]. The key trade-offs are [X vs Y]."
  * **Guided Questions:** "Does this decision align with our long-term goals for the project?"
  * **Action:** Await approval. If approved, update relevant Constitutional Rules (`.windsurf/rules/`) to reflect the new decision.
