"""Utilities for registering and executing engine benchmarks."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

BenchmarkCallable = Callable[[], Any]
BenchmarkRunner = Callable[[BenchmarkCallable], Any]


class BenchmarkRegistry:
    """Registry of named benchmark callables."""

    def __init__(self) -> None:
        self._benchmarks: dict[str, BenchmarkCallable] = {}

    def register(self, name: str, func: BenchmarkCallable) -> None:
        """Register ``func`` under ``name`` if not already taken."""
        if name in self._benchmarks:
            raise ValueError(f"Benchmark '{name}' is already registered.")
        self._benchmarks[name] = func

    def get(self, name: str) -> BenchmarkCallable:
        """Return the function associated with ``name``."""
        return self._benchmarks[name]

    @property
    def names(self) -> tuple[str, ...]:
        """Expose registered benchmark names in insertion order."""
        return tuple(self._benchmarks.keys())

    def run_all(self, runner: BenchmarkRunner | None = None) -> dict[str, Any]:
        """Execute every registered benchmark via ``runner``."""

        def _default_runner(func: BenchmarkCallable) -> Any:
            return func()

        effective_runner = runner or _default_runner
        results: dict[str, Any] = {}
        for name, func in self._benchmarks.items():
            results[name] = effective_runner(func)
        return results

    def run_with_pytest_codspeed(self, benchmark: BenchmarkRunner) -> dict[str, Any]:
        """Execute benchmarks using a ``pytest-codspeed`` style callable."""
        return self.run_all(benchmark)


# TECH_DEBT: Extend registry to capture benchmark metadata (tags, budgets).
# TECH_DEBT: Allow injecting benchmark-specific kwargs (e.g., warmup, rounds).
