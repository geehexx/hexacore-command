"""Benchmark registry specification tests."""

# ruff: noqa: S101
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pytest
from hexa_core.engine.benchmarking import BenchmarkRegistry


@dataclass
class RecordedCall:
    name: str
    result: object


class FakeBenchmarkRunner:
    def __init__(self: FakeBenchmarkRunner) -> None:
        self.calls: list[RecordedCall] = []

    def __call__(
        self: FakeBenchmarkRunner,
        func: Callable[..., object],
        *args: object,
        **kwargs: object,
    ) -> object:
        result = func(*args, **kwargs)
        self.calls.append(RecordedCall(func.__name__, result))
        return result


def describe_benchmark_registry_registration() -> None:
    def it_registers_and_lists_benchmarks() -> None:
        registry = BenchmarkRegistry()

        def alpha() -> int:
            return 1

        registry.register("alpha", alpha)
        assert registry.names == ("alpha",)
        assert registry.get("alpha") is alpha


def describe_benchmark_registry_duplicate_protection() -> None:
    def it_prevents_duplicate_registration() -> None:
        registry = BenchmarkRegistry()

        def alpha() -> int:
            return 1

        registry.register("alpha", alpha)
        with pytest.raises(ValueError):
            registry.register("alpha", alpha)


def describe_benchmark_registry_execution() -> None:
    def it_runs_registered_benchmarks_with_runner() -> None:
        registry = BenchmarkRegistry()

        def alpha() -> int:
            return 1

        def beta() -> int:
            return 2

        registry.register("alpha", alpha)
        registry.register("beta", beta)

        runner = FakeBenchmarkRunner()
        results = registry.run_all(runner)

        assert results == {"alpha": 1, "beta": 2}
        assert [call.name for call in runner.calls] == ["alpha", "beta"]

    def it_runs_benchmarks_with_pytest_style_runner() -> None:
        registry = BenchmarkRegistry()

        def alpha() -> int:
            return 1

        def beta() -> int:
            return 2

        registry.register("alpha", alpha)
        registry.register("beta", beta)

        runner = FakeBenchmarkRunner()
        results = registry.run_with_pytest_codspeed(runner)

        assert results == {"alpha": 1, "beta": 2}
        assert [call.name for call in runner.calls] == ["alpha", "beta"]
