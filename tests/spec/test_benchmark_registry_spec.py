from __future__ import annotations

from dataclasses import dataclass

import pytest
from hexa_core.engine.benchmarking import BenchmarkRegistry


@dataclass
class RecordedCall:
    name: str
    result: object


class FakeBenchmarkRunner:
    def __init__(self) -> None:
        self.calls: list[RecordedCall] = []

    def __call__(self, func, *args, **kwargs):
        result = func(*args, **kwargs)
        self.calls.append(RecordedCall(func.__name__, result))
        return result


def describe_benchmark_registry():
    def it_registers_and_lists_benchmarks() -> None:
        registry = BenchmarkRegistry()

        def alpha() -> int:
            return 1

        registry.register("alpha", alpha)
        assert registry.names == ("alpha",)
        assert registry.get("alpha") is alpha

    def it_prevents_duplicate_registration() -> None:
        registry = BenchmarkRegistry()

        def alpha() -> int:
            return 1

        registry.register("alpha", alpha)
        with pytest.raises(ValueError):
            registry.register("alpha", alpha)

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
