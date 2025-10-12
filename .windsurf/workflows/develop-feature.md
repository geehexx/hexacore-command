---
description: Develop Feature Workflow 
auto_execution_mode: 3
---

### **Phase 1: Planning and Contextual Analysis**

1. **Deconstruct the Request**  
  Summarize the user’s feature request, capturing core requirements, user stories, and acceptance criteria. Ask clarifying questions if critical details are missing. Deliver a concise synopsis before proceeding.
2. **Analyze the Existing Codebase**  
  Map the project structure and catalog every file expected to change or be created. Justify each file’s involvement by referencing relevant systems (e.g., ECS engine modules,  `Taskfile.yml`, documentation, workflows). Reuse existing patterns and data structures. Prefer  `mcp1_read_multiple_files`,  `mcp1_directory_tree`/`mcp1_directory_tree_with_sizes`, and `grep_search`  for efficient context gathering.
3. **Formulate an Implementation Plan**  
  Produce a detailed, sequential implementation plan covering every task, the intention behind it, and the files it will affect. Present this plan to the user and obtain explicit approval before entering Phase 2.

### **Phase 2: Implementation and In-line Quality Assurance**

4. **Execute the Implementation Plan**  
  Carry out tasks exactly as approved, honoring  `.windsurf/rules/`  (ECS, Event Bus, documentation lifecycle, testing mandates). Maintain TDD with  `spec-kit`  where applicable. Switch tools per `docs/tooling/editing-tools.md`  when editing protected paths.
5. **Generate Comprehensive Documentation**  
  Document new public interfaces and complex logic. Update living documentation as required, ensuring consistency with rule `.windsurf/rules/05_documentation_lifecycle.md`. Only modify constitutional rules after following the  `/propose-new-adr`  workflow.  
6. **Generate Unit Tests**  
  Create unit, spec, property, or benchmark tests as appropriate. Cover success, failure, and edge cases. Use  `tests/spec/`  for  `spec-kit`  scenarios and align with `ADR-0005` for performance-sensitive features.

### **Phase 3: Automated Validation and Self-Correction (Quality Gates)**

7. **Run Static Analysis**  
  Execute  `task lint:all`. Resolve every error or warning (Ruff, MyPy, PyMarkdown) and rerun until clean.
8. **Run Automated Tests**  
  Execute  `task test:unit`. Address failing tests before proceeding.
9. **Enforce Code Coverage Policy**  
  Run  `uv run pytest --cov=src/hexa_core --cov-report=term-missing`. Ensure new or modified code achieves ≥85% coverage. Add tests if coverage is insufficient.
10. **Execute Security Scan**  
  Run  `uv run pip-audit`. Remediate any critical/high findings before continuing. If the tool is unavailable, integrate it into the tooling (e.g., add  `pip-audit`  to dev dependencies and expose a Taskfile target). Document any temporary ignores (e.g., `--ignore-vuln GHSA-4xh5-x5gv-qwph`) and remove them once upstream fixes ship.

### **Phase 4: Finalization and Version Control**

11. **Update Project Documentation**  
  Amend  `README.md`,  `CONTRIBUTING.md`, and other user-facing docs to explain the new workflow and standards. Respect the Documentation Lifecycle rules.
12. **Format Commit Message**  
  Determine Conventional Commit  `type`/`scope`  and craft  `<type>(<scope>): <description>`  in present tense. Reference existing commit conventions and align with initiative context if relevant.
13. **Commit Changes**  
  Use MCP Git tools:  `mcp2_git_status`,  `mcp2_git_diff_unstaged`,  `mcp2_git_add`,  `mcp2_git_diff_staged`,  `mcp2_git_commit`. Stage only intended files and verify staged content before committing.
