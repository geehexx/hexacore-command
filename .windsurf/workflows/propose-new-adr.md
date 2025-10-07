---
description: Propose New ADR
auto_execution_mode: 3
---

**Objective:** To formalize a significant architectural decision.
**Process:**
    1. **Agent:** "I have identified a need for an architectural decision regarding [topic]."
    2. **Agent:** (Asks clarifying, high-level questions to the user to understand constraints and goals).
    3. **Agent:** "Based on your input, I will draft an ADR." (Generates the ADR in `docs/decisions/`).
    4. **CHECKPOINT: ADR Review.**
        - **Presentation:** "The draft ADR is ready for your review. It proposes [decision] to solve [problem]. The key trade-offs are [X vs Y]."
        - **Guided Questions:** "Does this decision align with our long-term goals for the project?"
        - **Action:** Await approval. If approved, update relevant Constitutional Rules (`.windsurf/rules/`) to reflect the new decision.
