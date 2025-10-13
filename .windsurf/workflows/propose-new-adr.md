---
description: Propose New ADR
auto_execution_mode: 3
---

# Propose New ADR Workflow

## Objective

Formalize a significant architectural decision.

## Process

1. **Agent:** "I have identified a need for an architectural decision regarding [topic]."
2. **Agent:** Ask clarifying, high-level questions to the user to understand constraints and goals.
3. **Agent:** "Based on your input, I will draft an ADR." Generate the ADR in `docs/decisions/`.
4. Checkpoint: ADR Review
   - Presentation: "The draft ADR is ready for your review. It proposes [decision] to solve [problem]. The key trade-offs are [X vs Y]."
   - Guided Questions: "Does this decision align with our long-term goals for the project?"
   - Action: Await approval. If approved, update relevant constitutional rules (`.windsurf/rules/`) to reflect the new decision.
