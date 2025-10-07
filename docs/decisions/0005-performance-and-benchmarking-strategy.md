# 5. Establish a Performance and Benchmarking Strategy

* **Status:** Accepted
* **Context:** While turn-based, the game's core loop involves complex calculations (pathfinding, ECS processing, script execution) that can scale in complexity. We must ensure the engine remains performant as features are added. This was a key learning from the `traffic-simulator` project.
* **Decision:**
  1. **Tooling:** We will use `pytest-benchmark` for all performance measurement.
  2. **Requirement:** Performance-sensitive systems MUST be accompanied by benchmark tests located in `tests/benchmarks/`.
  3. **Initial Focus:** The initial systems identified for benchmarking are:
      * The main ECS `world.process()` loop.
      * The `find_path` helper operation.
      * The `ScriptRunner`'s parsing and execution steps.
  4. **Performance Budget (MVP):** A full turn involving 50 entities and 10 script executions must complete its engine processing in under **100 milliseconds** on the CI runner.
* **Consequences:** Performance becomes a measurable and testable requirement, preventing regressions and guiding optimization efforts.
