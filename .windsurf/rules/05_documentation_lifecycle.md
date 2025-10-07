---
trigger: glob
description: "Governs how documentation is created, maintained, and retired. This is a meta-rule about the development process itself."
globs: docs/**/*.md
---

# Rule: Documentation Lifecycle & Decision Making

1. **Constitutional Documents (`.windsurf/rules/`):** Timeless, architectural laws. They are only changed if an Architectural Decision Record (ADR) explicitly modifies a core principle. The workflow for proposing such a change must be followed.
2. **Living Documentation (`docs/*.md`):** Detailed explanations of the current implementation. As you implement features, you MUST populate these documents with the "how" and "why" of the final, working implementation. They must be kept in sync with the `main` branch.
3. **Initiative Documents (`docs/initiatives/*.md`, `docs/decisions/*.md`):**
    * **Roadmaps:** Temporary checklists. Propose archival upon completion.
    * **Architectural Decision Records (ADRs):** Your primary tool for proposing and recording significant technical decisions. Follow the template in `ADR-0001`. Use the `[PLAN] Propose New ADR` workflow.
