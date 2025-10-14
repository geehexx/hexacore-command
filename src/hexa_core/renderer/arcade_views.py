"""Arcade view adapters for renderer states."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from hexa_core.engine.event_bus import EventBus
from hexa_core.renderer import events
from hexa_core.renderer.renderer import HexaRenderer, RendererState

try:  # pragma: no cover - imported conditionally during tests
    import arcade
except ModuleNotFoundError:  # pragma: no cover - spec-kit provides stubs
    arcade = None  # type: ignore


@dataclass(slots=True)
class MissionBriefingCallbacks:
    accept: Callable[[], None]
    decline: Callable[[], None]


@dataclass(slots=True)
class GameplayCallbacks:
    exit_gameplay: Callable[[], None]


class BaseScreen:  # pragma: no cover - relies on Arcade runtime
    def __init__(self: BaseScreen, renderer: HexaRenderer) -> None:
        self.renderer = renderer
        self.window: arcade.Window | None = None

    def on_show(self: BaseScreen) -> None:
        if arcade is not None:
            arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self: BaseScreen) -> None:
        if arcade is None:
            return
        arcade.start_render()


class MainMenuScreen(BaseScreen):  # pragma: no cover - UI tested via renderer state
    def __init__(self: MainMenuScreen, renderer: HexaRenderer, event_bus: EventBus) -> None:
        super().__init__(renderer)
        self.event_bus = event_bus

    def on_key_press(self: MainMenuScreen, symbol: int, modifiers: int) -> None:  # noqa: ARG002 - placeholder input handling
        if symbol == arcade.key.ENTER:
            self.event_bus.publish(events.MISSION_BRIEFING_REQUESTED, {})
        elif symbol == arcade.key.ESCAPE:
            self.event_bus.publish(events.GAMEPLAY_EXITED, {})


class MissionBriefingScreen(BaseScreen):
    def __init__(self: MissionBriefingScreen, renderer: HexaRenderer, callbacks: MissionBriefingCallbacks) -> None:
        super().__init__(renderer)
        self.callbacks = callbacks

    def confirm_mission(self: MissionBriefingScreen) -> None:
        self.callbacks.accept()

    def cancel_mission(self: MissionBriefingScreen) -> None:
        self.callbacks.decline()


class GameplayScreen(BaseScreen):
    def __init__(self: GameplayScreen, renderer: HexaRenderer, callbacks: GameplayCallbacks) -> None:
        super().__init__(renderer)
        self.callbacks = callbacks

    def exit_gameplay(self: GameplayScreen) -> None:
        self.callbacks.exit_gameplay()


def build_mission_briefing_screen(renderer: HexaRenderer, event_bus: EventBus) -> MissionBriefingScreen:
    view = MissionBriefingScreen(
        renderer,
        MissionBriefingCallbacks(
            accept=lambda: event_bus.publish(events.MISSION_ACCEPTED, {}),
            decline=lambda: event_bus.publish(events.MISSION_DECLINED, {}),
        ),
    )
    return view


def build_gameplay_screen(renderer: HexaRenderer, event_bus: EventBus) -> GameplayScreen:
    view = GameplayScreen(
        renderer,
        GameplayCallbacks(exit_gameplay=lambda: event_bus.publish(events.GAMEPLAY_EXITED, {})),
    )
    return view


def reconcile_view(renderer: HexaRenderer, event_bus: EventBus, current_view: BaseScreen | None) -> BaseScreen:
    state = renderer.current_state
    if state is RendererState.MISSION_BRIEFING:
        return build_mission_briefing_screen(renderer, event_bus)
    if state is RendererState.GAMEPLAY:
        return build_gameplay_screen(renderer, event_bus)
    return MainMenuScreen(renderer, event_bus)
