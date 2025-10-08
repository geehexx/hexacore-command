# Initiative 0004: Behavior-Driven Development with pytest-bdd

* **Objective:** Introduce Behavior-Driven Development (BDD) for feature-level testing to improve clarity, collaboration, and ensure tests are aligned with user-facing requirements.
* **Status:** In Progress

## Plan

1. **Add Dependency:** Ensure [`pytest-bdd`](https://pytest-bdd.readthedocs.io/) is part of the `[project.optional-dependencies]` `dev` group in `pyproject.toml`.
2. **Establish Two-Tiered Testing Strategy:**
    * Update `.windsurf/rules/06_testing_and_tooling.md` to formalize a two-tiered testing approach:
        * **Behavior-Level Tests (BDD):** High-level acceptance and integration tests will be written using `pytest-bdd` in Gherkin (`.feature`) files. These live in `tests/features/`.
        * **Unit-Level Tests (Spec-Driven):** Low-level unit tests continue to use the `spec-kit` (`pytest-describe`) style in `tests/spec/`.
3. **Create Scaffolding:**
    * Provide canonical feature files in `tests/features/`, starting with `bot_movement.feature`.
    * Implement corresponding step definitions (e.g., `tests/features/test_bot_movement_bdd.py`) that exercise real engine services (event bus, world) instead of placeholders.
4. **Update Taskfile:** Maintain the dedicated `test:bdd` task in `Taskfile.yml` to run `pytest tests/features`.
5. **Document Practices:** Capture BDD authoring guidance in the living documentation set alongside CodSpeed usage notes.

## TODO

* Define a strategy for testing features that require visual interaction with the game, as no tooling for this is currently defined.

## Affected Files

* `pyproject.toml`
* `.windsurf/rules/06_testing_and_tooling.md`
* `Taskfile.yml`
* New files within a new `tests/features/` directory.

## Success Criteria

* The `pytest-bdd` dependency remains in the development toolchain.
* `.windsurf/rules/06_testing_and_tooling.md` calls out the two-tiered strategy that includes BDD coverage.
* `tests/features/bot_movement.feature` and `tests/features/test_bot_movement_bdd.py` exercise engine event scheduling without placeholders.
* Living documentation references (BDD playbook plus CodSpeed benchmarking guide) are published and linked from initiative artifacts.

## Next Steps

* Add scenarios for script error handling and combat resolution once those systems publish stable events.
* Model multi-turn behaviors (initiative, cooldowns) using background sections to validate upcoming turn manager logic.
