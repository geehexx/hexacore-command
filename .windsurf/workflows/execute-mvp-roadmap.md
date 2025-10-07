---
description: Execute MVP Roadmap
auto_execution_mode: 3
---

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