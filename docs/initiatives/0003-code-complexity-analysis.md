# Initiative 0003: Code Complexity Analysis with Radon

* **Objective:** Integrate static analysis for code complexity to enforce maintainability standards and prevent overly complex code from being committed.
* **Status:** Proposed

## Context

* `radon` computes cyclomatic complexity, maintainability index, Halstead metrics, and raw code statistics, and can be configured via command-line flags or shared configuration files for repeatable analysis.[^radon-intro][^radon-cli]
* `xenon` wraps `radon` to enforce maximum complexity thresholds, exiting with non-zero status suitable for pre-commit and CI enforcement.[^xenon]
* Broader quality efforts benefit from tracking complementary metrics such as cognitive complexity, coupling, and inheritance depth to surface readability and design risks early.[^dailydev][^sonar-cognitive][^sonar-clean-code]
* Maintainability index values can be misleading when interpreted without calibration; averages hide hotspots and the formula is highly size-dependent.[^maintainability]

## Plan

### Metric Coverage Baseline

* Add [`radon`](https://radon.readthedocs.io/) as a development dependency and document usage patterns for `cc`, `mi`, `hal`, and `raw` commands.
* Define default scopes and excludes in `radon.cfg` (or `setup.cfg`) to ensure deterministic metric reporting across contributors.[^radon-cli]
* Capture maintainability index caveats within initiative risk notes so the team treats MI as advisory rather than a lone gate.[^maintainability]

### Tooling and Automation Integration

* Introduce a pre-commit hook that executes `xenon --max-absolute=B --max-modules=A --max-average=A` to hard-stop commits exceeding the agreed complexity budget.[^xenon]
* Expose a Taskfile target (e.g., `task lint:complexity`) that runs both `radon cc -a` and `radon mi` over the repository to track trends during CI and manual validation.
* Document how to extend tooling later with cognitive complexity dashboards (e.g., Sonar-based pipelines) without blocking the initial rollout.[^sonar-cognitive]

### Process and Reporting Enhancements

* Establish a cadence (per-iteration) for exporting radon summaries to initiative status updates, highlighting modules with complexity rank `C` or worse and following up with refactoring tickets when feasible.
* Encourage pairing radon output with qualitative reviews focused on readability and control-flow depth, referencing SonarSource clean-code guidance for reducing cognitive load.[^sonar-clean-code]

### Risk Management and Follow-up

* Flag large functions that slip past average-based checks by tracking the heaviest tails separately and aggregating hotspots into living documentation.
* Monitor false positives or friction from the pre-commit hook, adjusting thresholds only after a retro documenting the trade-offs.
* Re-evaluate maintainability index usefulness after initial adoption; consider replacing it with richer maintainability signals if MI readings prove inconsistent.[^maintainability]

## Affected Files

* `pyproject.toml`
* `.pre-commit-config.yaml`
* `.windsurf/rules/06_testing_and_tooling.md`
* `radon.cfg` (new, if shared defaults are required)
* `Taskfile.yml`

## Success Criteria

* `radon` is available in the development toolchain with shared configuration and documentation updates completed.
* The `xenon` pre-commit hook (or equivalent Taskfile target) fails when code exceeds the agreed `B` complexity ceiling for blocks or `A` for modules.
* Task automation and documentation cover how to run `radon cc`, `radon mi`, and the follow-up reporting workflow.
* Initiative risk notes highlight maintainability index limitations, and the team captures complexity hotspots for follow-up work.

## Follow-up Actions

* Socialize the complexity dashboard expectations during the next architecture sync and capture feedback for iteration.
* Track adoption metrics (hook pass/fail counts, hotspot backlog entries) to inform future enhancements such as cognitive complexity integration.
* Launch a targeted documentation lint remediation effort:
  * Open a follow-up chore (or new initiative) to resolve the existing `pymarkdown` backlog across key files such as `.windsurf/rules/06_testing_and_tooling.md`, `docs/renderer.md`, `docs/testing/pytest_codspeed.md`, and `docs/tooling/*.md`.
  * Batch fixes by directory, validating each pass with `uv run pre-commit run pymarkdown --all-files` to avoid regressions while modernizing formatting (headings, list indentation, fenced-block spacing, and line length wraps).
  * Capture completion checkpoints in initiative status reports so complexity gating and documentation linting converge in CI timelines.
* Monitor `ScriptRunner` maintainability (`radon mi`) during refactors to ensure average complexity continues trending down and revisit thresholds after two sprints of adoption data.

[^radon-intro]: [Introduction to Code Metrics — Radon documentation](https://radon.readthedocs.io/en/latest/intro.html)
[^radon-cli]: [Command-line Usage — Radon documentation](https://radon.readthedocs.io/en/latest/commandline.html)
[^xenon]: [Xenon README — radon-based enforcement](https://raw.githubusercontent.com/rubik/xenon/master/README.rst)
[^dailydev]: [7 Code Complexity Metrics Developers Must Track — daily.dev](https://daily.dev/blog/7-code-complexity-metrics-developers-must-track)
[^sonar-cognitive]: [Cognitive Complexity — SonarSource resource](https://www.sonarsource.com/resources/cognitive-complexity/)
[^sonar-clean-code]: [5 Clean Code Tips for Reducing Cognitive Complexity — SonarSource blog](https://www.sonarsource.com/blog/5-clean-code-tips-for-reducing-cognitive-complexity/)
[^maintainability]: [Think Twice Before Using the “Maintainability Index” — Arie van Deursen](https://avandeursen.com/2014/08/29/think-twice-before-using-the-maintainability-index/)
