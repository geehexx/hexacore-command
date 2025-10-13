"""Combat system specification tests."""

from __future__ import annotations

# ruff: noqa: S101
from collections import deque
from typing import cast

import pytest
from hexa_core.engine.components import CombatIntentComponent, StatsComponent
from hexa_core.engine.event_bus import EventBus
from hexa_core.engine.world import GameWorld


def describe_combat_system() -> None:
    def it_applies_damage_and_publishes_event() -> None:
        bus = EventBus()
        world = GameWorld(event_bus=bus)

        from hexa_core.engine.systems.combat_system import CombatSystem

        combat_system = CombatSystem(event_bus=bus)
        world.add_processor(combat_system)

        attacker = cast(int, world.create_entity())
        target = cast(int, world.create_entity())
        world.add_component(attacker, StatsComponent(health=100, speed=50, processor=100))
        world.add_component(target, StatsComponent(health=60, speed=40, processor=80))
        world.add_component(attacker, CombatIntentComponent(target=target, damage=35))

        captured: deque[tuple[str, dict[str, object]]] = deque()
        world.subscribe_event("engine.combat.resolved", lambda event, payload: captured.append((event, payload)))

        world.process()

        target_stats = cast(StatsComponent, world.component_for_entity(target, StatsComponent))
        assert target_stats.health == 25
        assert world.try_component(attacker, CombatIntentComponent) is None
        assert list(captured) == [
            (
                "engine.combat.resolved",
                {
                    "attacker_id": attacker,
                    "target_id": target,
                    "damage": 35,
                    "remaining_health": 25,
                    "defeated": False,
                },
            )
        ]

    def it_marks_target_defeated_when_health_drops_to_zero() -> None:
        bus = EventBus()
        world = GameWorld(event_bus=bus)

        from hexa_core.engine.systems.combat_system import CombatSystem

        combat_system = CombatSystem(event_bus=bus)
        world.add_processor(combat_system)

        attacker = cast(int, world.create_entity())
        target = cast(int, world.create_entity())
        world.add_component(attacker, StatsComponent(health=70, speed=30, processor=60))
        world.add_component(target, StatsComponent(health=40, speed=20, processor=40))
        world.add_component(attacker, CombatIntentComponent(target=target, damage=50))

        captured: deque[tuple[str, dict[str, object]]] = deque()
        world.subscribe_event("engine.combat.resolved", lambda event, payload: captured.append((event, payload)))

        world.process()

        target_stats = cast(StatsComponent, world.component_for_entity(target, StatsComponent))
        assert target_stats.health == 0
        assert list(captured) == [
            (
                "engine.combat.resolved",
                {
                    "attacker_id": attacker,
                    "target_id": target,
                    "damage": 50,
                    "remaining_health": 0,
                    "defeated": True,
                },
            )
        ]

        with pytest.raises(RuntimeError):
            world.consume_turn(target)  # ensure no unintended side effects
