"""Renderer app specifications."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from hexa_core.engine.event_bus import EventBus
from hexa_core.renderer import events
from hexa_core.renderer.app import RendererApp, create_renderer_app
from hexa_core.renderer.renderer import HexaRenderer, RendererState


class RecordingEventBus(EventBus):
    def __init__(self: RecordingEventBus) -> None:
        super().__init__()
        self.published: list[tuple[str, dict[str, object]]] = []

    def publish(self: RecordingEventBus, event_type: str, payload: dict[str, object]) -> None:
        self.published.append((event_type, payload))
        super().publish(event_type, payload)


class StubWindow:
    def __init__(
        self: StubWindow,
        width: int,
        height: int,
        title: str,
        *,
        update_rate: float | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.update_rate = update_rate
        self.visible_view: object | None = None

    def show_view(self: StubWindow, view: object) -> None:
        self.visible_view = view
        if hasattr(view, "window"):
            view.window = self
        if hasattr(view, "on_show"):
            view.on_show()


class StubArcade(SimpleNamespace):
    def __init__(self: StubArcade) -> None:
        super().__init__()
        self.Window = StubWindow
        self.View = object
        self.key = SimpleNamespace(ENTER=65293, ESCAPE=65307)
        self.run_calls: list[None] = []
        self.background_color: tuple[int, int, int, int] | None = None
        self.color = SimpleNamespace(BLACK=(0, 0, 0, 255))

    def run(self: StubArcade) -> None:
        self.run_calls.append(None)

    def set_background_color(self: StubArcade, color: tuple[int, int, int, int]) -> None:
        self.background_color = color

    def start_render(self: StubArcade) -> None:
        return None


@pytest.fixture()
def stub_arcade(monkeypatch: pytest.MonkeyPatch) -> StubArcade:
    stub = StubArcade()
    monkeypatch.setattr("hexa_core.renderer.app.arcade", stub, raising=False)
    monkeypatch.setattr("hexa_core.renderer.arcade_views.arcade", stub, raising=False)
    return stub


@pytest.fixture()
def renderer_app(stub_arcade: StubArcade) -> RendererApp:
    bus = RecordingEventBus()
    return create_renderer_app(event_bus=bus)


def describe_renderer_app() -> None:
    def it_builds_renderer_app_with_defaults(stub_arcade: StubArcade) -> None:
        app = create_renderer_app()

        assert isinstance(app.renderer, HexaRenderer)
        assert isinstance(app.event_bus, EventBus)
        assert app.window_title == "Hexa-Core Command"

    def it_launches_window_and_registers_handlers(renderer_app: RendererApp, stub_arcade: StubArcade) -> None:
        renderer_app.launch()

        assert isinstance(renderer_app.renderer, HexaRenderer)
        assert isinstance(renderer_app.event_bus, EventBus)
        assert isinstance(renderer_app.current_window, StubWindow)
        assert isinstance(stub_arcade.run_calls, list) and len(stub_arcade.run_calls) == 1
        registered = renderer_app.event_bus.subscribers(events.MISSION_BRIEFING_REQUESTED)
        assert registered

    def it_switches_to_mission_briefing_on_event(renderer_app: RendererApp) -> None:
        renderer_app.launch()
        payload = {
            "name": "Operation Dawn",
            "objectives": ["Secure landing zone"],
            "grid_size": {"width": 12, "height": 10},
        }

        handler = renderer_app.event_bus.subscribers(events.MISSION_BRIEFING_REQUESTED)[0]
        handler(events.MISSION_BRIEFING_REQUESTED, payload)

        assert renderer_app.renderer.current_state is RendererState.MISSION_BRIEFING
        assert renderer_app.current_window.visible_view.__class__.__name__ == "MissionBriefingScreen"

    def it_dispatches_mission_acceptance(renderer_app: RendererApp) -> None:
        renderer_app.launch()
        payload = {
            "name": "Operation Dawn",
            "objectives": ["Secure landing zone"],
            "grid_size": {"width": 12, "height": 10},
        }
        handler = renderer_app.event_bus.subscribers(events.MISSION_BRIEFING_REQUESTED)[0]
        handler(events.MISSION_BRIEFING_REQUESTED, payload)
        briefing_view = renderer_app.current_window.visible_view

        briefing_view.confirm_mission()

        bus = renderer_app.event_bus
        assert bus.published[-1][0] == events.MISSION_ACCEPTED

    def it_transitions_to_gameplay(renderer_app: RendererApp) -> None:
        renderer_app.launch()
        payload = {
            "name": "Operation Dawn",
            "objectives": [],
            "grid_size": {"width": 12, "height": 10},
        }
        briefing_handler = renderer_app.event_bus.subscribers(events.MISSION_BRIEFING_REQUESTED)[0]
        briefing_handler(events.MISSION_BRIEFING_REQUESTED, payload)
        gameplay_handler = renderer_app.event_bus.subscribers(events.GAMEPLAY_ACTIVATED)[0]

        gameplay_handler(events.GAMEPLAY_ACTIVATED, {})

        assert renderer_app.renderer.current_state is RendererState.GAMEPLAY
        assert renderer_app.current_window.visible_view.__class__.__name__ == "GameplayScreen"

    def it_publishes_exit_event(renderer_app: RendererApp) -> None:
        renderer_app.launch()
        payload = {
            "name": "Operation Dawn",
            "objectives": [],
            "grid_size": {"width": 12, "height": 10},
        }
        briefing_handler = renderer_app.event_bus.subscribers(events.MISSION_BRIEFING_REQUESTED)[0]
        briefing_handler(events.MISSION_BRIEFING_REQUESTED, payload)
        gameplay_handler = renderer_app.event_bus.subscribers(events.GAMEPLAY_ACTIVATED)[0]
        gameplay_handler(events.GAMEPLAY_ACTIVATED, {})
        gameplay_view = renderer_app.current_window.visible_view

        gameplay_view.exit_gameplay()

        bus = renderer_app.event_bus
        assert bus.published[-1][0] == events.GAMEPLAY_EXITED
