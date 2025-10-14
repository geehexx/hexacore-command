# Testing Playbook

## Metadata

- **Topic:** Hexa-Core Command Testing Architecture
- **Keywords:** testing, spec-kit, pytest-bdd, hypothesis, codspeed
- **Related ADRs:** [ADR-0005](../decisions/0005-performance-and-benchmarking-strategy.md)
- **Key Libraries:**
  - [`pytest`](https://docs.pytest.org/)
  - [`spec-kit`](https://github.com/github/spec-kit)
  - [`pytest-bdd`](https://pytest-bdd.readthedocs.io/)
  - [`hypothesis`](https://hypothesis.readthedocs.io/)
  - [`pytest-codspeed`](https://docs.codspeed.io/docs/pytest/overview)
  - [`pytest-xdist`](https://pytest-xdist.readthedocs.io/)

## Overview

Hexa-Core Command relies on a layered testing strategy to keep the engine deterministic and observable.
This playbook explains how each testing style is applied and which automation targets exercise them.

## Spec Tests (`tests/spec/`)

- **Purpose:** Drive engine code with TDD using `spec-kit` (`pytest-describe`).
- **Structure:** Each file defines `describe_*` blocks with nested behavior-focused tests.
- **Execution:** Run `task test:spec` for the spec-only subset, `task test:unit` for the entire suite, or `task test:unit:parallel` when you need accelerated spec-kit feedback.

## Behavior-Driven Development (`tests/features/`)

- **Purpose:** Express player-visible behavior via Gherkin scenarios executed with `pytest-bdd`.
- **Structure:** Feature files live alongside step definition modules. Steps must integrate with real engine services (e.g., `GameWorld`, `EventBus`) and exercise production systems such as `MovementSystem`.
- **Execution:** Run `task test:bdd` or target individual features with `uv run pytest tests/features/<feature>.py`.
- **Backgrounds & Fixtures:** Use `Background` sections or reusable fixtures to provision worlds, processors, and entity scaffolding so each scenario remains declarative.
- **Event Assertions:** Subscribe to engine events within step definitions to capture payloads for verification instead of asserting on mocks.
- **Reference:** See `tests/features/bot_movement.feature` and `tests/features/test_bot_movement_bdd.py` for an end-to-end movement example. Additional authoring guidance lives in `docs/testing/bdd_playbook.md`, and initiative history is stored under `docs/initiatives/archive/0004-behavior-driven-development.md`.

## Property-Based Testing (`tests/property/`)

- **Purpose:** Ensure algorithms remain correct across broad input domains using Hypothesis strategies.
- **Structure:** Property tests share common strategy builders per datatype or system. Store helpers alongside tests when reuse is limited.
- **Execution:** Run `task test:property` for the property suite. Integrate property tests into CI by adding the task to composite workflows as needed. Use `task test:unit:cov` or `task coverage:report` to ensure invariants stay covered across the whole engine.
- **Reference:** `tests/property/test_hex_coord_property.py` validates `HexCoord` symmetry and neighbor relationships.
- **Next Steps:** Extend property suites to cover movement and combat systems once their implementations are stabilized so invariants around range, cooldowns, and damage can be encoded.

## Performance Benchmarks (`tests/benchmarks/`)

- **Purpose:** Track performance regressions through CodSpeed-backed benchmarks executing in parallel via `pytest-xdist`.
- **Structure:** Register benchmark callables in modules and execute them through `BenchmarkRegistry`. The new `tests/benchmarks/test_world_process_codspeed.py` scenario stresses `GameWorld.process()` using a lightweight `TickProcessor`.
- **Execution:** Run `task test:benchmarks` (CodSpeed) or `task ci:benchmarks` during CI. For diagnosing CodSpeed issues without parallelism, reach for `task test:benchmarks:serial`.
- **Reference:** Consult `docs/testing/pytest_codspeed.md` for deeper integration guidance.

## Workflow Summary

| Suite | Command | Notes |
| --- | --- | --- |
| Spec | `task test:spec` | Unit-level coverage with `spec-kit`. |
| BDD | `task test:bdd` | User-facing acceptance behavior. |
| Property | `task test:property` | Hypothesis-driven invariants. |
| Benchmarks | `task test:benchmarks` / `task test:benchmarks:serial` | CodSpeed benchmarking (parallel / serial). |

Keep this table aligned with `Taskfile.yml` whenever new suites or commands are introduced.
