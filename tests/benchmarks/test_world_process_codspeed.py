"""CodSpeed benchmarks exercising the ECS world processing loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import esper

if TYPE_CHECKING:
    from pytest import BenchmarkFixture

from hexa_core.engine.benchmarking import BenchmarkRegistry
from hexa_core.engine.world import GameWorld

registry = BenchmarkRegistry()


@dataclass(slots=True)
class TickComponent:
    """Lightweight component for exercising processor workloads."""

    value: int = 0


class TickProcessor(esper.Processor):
    """Increment component counters during world processing."""

    def __init__(self: TickProcessor) -> None:
        super().__init__()
        self.total_ticks: int = 0

    def process(self: TickProcessor) -> None:  # pragma: no cover - exercised via CodSpeed
        total = 0
        for _, component in esper.get_component(TickComponent):
            component.value += 1
            total += component.value
        self.total_ticks = total


def _world_process_tick_accumulation() -> int:
    """Baseline benchmark that stresses entity processing throughput."""

    world = GameWorld()
    processor = TickProcessor()
    world.add_processor(processor)

    for index in range(128):
        entity_id = world.create_entity()
        world.add_component(entity_id, TickComponent(index))

    world.process()
    return processor.total_ticks


registry.register("world_process_tick_accumulation", _world_process_tick_accumulation)


def test_world_process_benchmark_executes(benchmark: BenchmarkFixture) -> None:
    """Ensure benchmark registry entries run under pytest-codspeed."""

    results = registry.run_with_pytest_codspeed(benchmark)
    if "world_process_tick_accumulation" not in results:
        msg = "CodSpeed registry did not execute world_process benchmark"
        raise AssertionError(msg)
    if results["world_process_tick_accumulation"] < 0:
        msg = "CodSpeed benchmark produced a negative tick accumulation"
        raise AssertionError(msg)
