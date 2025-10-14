"""Utilities for registering and executing engine benchmarks."""

from __future__ import annotations

from collections.abc import Callable
from typing import Self, overload

BenchmarkCallable = Callable[[], object]
BenchmarkRunner = Callable[[BenchmarkCallable], object]


class BenchmarkRegistry:
    """Registry of named benchmark callables."""

    def __init__(self: Self) -> None:
        self._benchmarks: dict[str, BenchmarkCallable] = {}

    @overload
    def register(self: Self, name: str, func: BenchmarkCallable) -> BenchmarkCallable: ...

    @overload
    def register(self: Self, name: str) -> Callable[[BenchmarkCallable], BenchmarkCallable]: ...

    def register(
        self: Self,
        name: str | None = None,
        func: BenchmarkCallable | None = None,
    ) -> BenchmarkCallable | Callable[[BenchmarkCallable], BenchmarkCallable]:
        """Register ``func`` under ``name``.

        Can be used either as ``register("name", func)`` or ``@register("name")``.
        """

        def _perform_registration(target_name: str, target_func: BenchmarkCallable) -> BenchmarkCallable:
            if target_name in self._benchmarks:
                raise ValueError(f"Benchmark '{target_name}' is already registered.")
            self._benchmarks[target_name] = target_func
            return target_func

        if func is not None:
            if name is None:
                raise ValueError("Benchmark name must be provided when registering directly.")
            return _perform_registration(name, func)

        if name is None:
            raise ValueError("Benchmark name must be provided for decorator usage.")

        def decorator(target: BenchmarkCallable) -> BenchmarkCallable:
            return _perform_registration(name, target)

        return decorator

    def get(self: Self, name: str) -> BenchmarkCallable:
        """Return the function associated with ``name``."""
        return self._benchmarks[name]

    @property
    def names(self: Self) -> tuple[str, ...]:
        """Expose registered benchmark names in insertion order."""
        return tuple(self._benchmarks.keys())

    def run_all(self: Self, runner: BenchmarkRunner | None = None) -> dict[str, object]:
        """Execute every registered benchmark via ``runner``."""

        def _default_runner(func: BenchmarkCallable) -> object:
            """Execute ``func`` directly when no explicit runner is provided."""
            return func()

        effective_runner: BenchmarkRunner = runner or _default_runner
        results: dict[str, object] = {}
        for name, func in self._benchmarks.items():
            results[name] = effective_runner(func)
        return results

    def run_with_pytest_codspeed(self: Self, benchmark: BenchmarkRunner) -> dict[str, object]:
        """Execute benchmarks using a ``pytest-codspeed`` style callable."""
        return self.run_all(benchmark)


# TECH_DEBT: Extend registry to capture benchmark metadata (tags, budgets).
# TECH_DEBT: Allow injecting benchmark-specific kwargs (e.g., warmup, rounds).
