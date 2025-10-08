# Initiative 0005: Parallel Test Execution and CodSpeed Migration

* **Objective:** Significantly reduce the runtime of the test and benchmark suites by enabling parallel execution, ensuring a faster feedback loop for developers and CI.
* **Status:** Proposed

## Plan

1. **Migrate Benchmarking Tool:**
    * Remove `pytest-benchmark` from the `dev` dependencies in `pyproject.toml`.
    * Add [`pytest-codspeed`](https://docs.codspeed.io/docs/pytest/overview) to the `dev` dependencies. `pytest-codspeed` is compatible with parallel execution.
2. **Enable Parallel Execution:**
    * Add [`pytest-xdist`](https://pytest-xdist.readthedocs.io/) to the `dev` dependencies in `pyproject.toml`.
3. **Update Automation Tasks:**
    * Modify `Taskfile.yml` to introduce parallel execution commands:
        * Add a new task `test:unit:parallel` that runs `pytest -n auto tests/spec/`.
        * Update the `test:benchmarks` and `ci:benchmarks` tasks to execute `pytest --codspeed -n auto tests/benchmarks/`.
4. **Update Documentation:**
    * In `docs/decisions/0005-performance-and-benchmarking-strategy.md`, replace all mentions of `pytest-benchmark` with `pytest-codspeed` and update helper references accordingly.
    * In `.windsurf/rules/06_testing_and_tooling.md`, update the description of performance testing to reference `pytest-codspeed`.

## Affected Files

* `pyproject.toml`
* `Taskfile.yml`
* `docs/decisions/0005-performance-and-benchmarking-strategy.md`
* `.windsurf/rules/06_testing_and_tooling.md`

## Success Criteria

* Dependencies are updated.
* The `Taskfile.yml` provides commands for running unit tests and benchmarks in parallel.
* All relevant documentation is updated to reflect the new tooling.

## Next Steps

* Populate `tests/benchmarks/` with CodSpeed scenarios that exercise `world.process()` and forthcoming pathfinding routines once those systems stabilize.
* Capture benchmark result baselines in CI artifacts so regressions can be compared release over release.
