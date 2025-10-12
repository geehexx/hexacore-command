"""Hexa-Script runner specifications."""

from __future__ import annotations

# ruff: noqa: S101
import pytest
from hexa_core.engine.script_runner import ScriptRunner


def describe_script_runner() -> None:
    def it_sets_variables_and_halts_on_end() -> None:
        runner = ScriptRunner()
        runner.load(
            '\n'.join(
                [
                    'SET "target" 3',
                    'END',
                ]
            )
        )
        context: dict[str, object] = {"variables": {}}

        runner.execute(context)

        variables = context["variables"]
        assert isinstance(variables, dict)
        assert variables["target"] == 3

    def it_evaluates_condition_and_loops_until_threshold() -> None:
        runner = ScriptRunner()
        runner.load(
            '\n'.join(
                [
                    'SET "counter" 3',
                    'LABEL "loop"',
                    'SET "counter" ( counter - 1 )',
                    'IF counter > 0 THEN GOTO "loop"',
                    'END',
                ]
            )
        )
        context: dict[str, object] = {"variables": {}}

        runner.execute(context)

        variables = context["variables"]
        assert isinstance(variables, dict)
        assert variables["counter"] == 0

    def it_records_action_invocations() -> None:
        runner = ScriptRunner()
        runner.load(
            '\n'.join(
                [
                    'ACTION "move" "north"',
                    'END',
                ]
            )
        )
        context: dict[str, object] = {"variables": {}, "actions": []}

        runner.execute(context)

        actions = context["actions"]
        assert isinstance(actions, list)
        assert actions == [("move", ("north",))]

    def it_raises_runtime_error_for_unknown_label() -> None:
        runner = ScriptRunner()
        runner.load(
            '\n'.join(
                [
                    'GOTO "missing"',
                    'END',
                ]
            )
        )

        with pytest.raises(RuntimeError):
            runner.execute({"variables": {}})
