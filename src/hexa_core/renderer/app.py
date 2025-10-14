"""Arcade application bootstrap for Hexa-Core Command."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from hexa_core.engine.event_bus import EventBus
from hexa_core.renderer import arcade_views, events
from hexa_core.renderer.renderer import HexaRenderer, RendererState

try:  # pragma: no cover - guarded for spec-kit stubs
    import arcade
except ModuleNotFoundError:  # pragma: no cover - test doubles provide arcade
    arcade = None  # type: ignore


WindowFactory = Callable[..., Any]


@dataclass(slots=True)
class RendererApp:
    renderer: HexaRenderer
    event_bus: EventBus
    width: int = 1280
    height: int = 720
    window_title: str = "Hexa-Core Command"
    update_rate: float | None = 1 / 60
    window_factory: WindowFactory | None = None
    current_window: Any | None = field(default=None, init=False)
    _current_view: arcade_views.BaseScreen | None = field(default=None, init=False)

    def __post_init__(self: RendererApp) -> None:
        self._register_handlers()

    def launch(self: RendererApp) -> None:
        if arcade is None:  # pragma: no cover - requires real runtime
            raise RuntimeError("Arcade runtime is unavailable")
        factory = self.window_factory or arcade.Window
        kwargs: dict[str, Any] = {}
        if self.update_rate is not None:
            kwargs["update_rate"] = self.update_rate
        self.current_window = factory(self.width, self.height, self.window_title, **kwargs)
        self._transition_to_state(self.renderer.current_state)
        arcade.run()

    def _register_handlers(self: RendererApp) -> None:
        self.event_bus.subscribe(events.MISSION_BRIEFING_REQUESTED, self._on_mission_briefing_requested)
        self.event_bus.subscribe(events.GAMEPLAY_ACTIVATED, self._on_gameplay_activated)
        self.event_bus.subscribe(events.GAMEPLAY_EXITED, self._on_gameplay_exited)

    def _on_mission_briefing_requested(self: RendererApp, _: str, payload: dict[str, Any]) -> None:
        self.renderer.load_mission_briefing(payload)
        self._transition_to_state(RendererState.MISSION_BRIEFING)

    def _on_gameplay_activated(self: RendererApp, _: str, payload: dict[str, Any]) -> None:  # noqa: ARG002 - future use
        self.renderer.proceed_to_gameplay()
        self._transition_to_state(RendererState.GAMEPLAY)

    def _on_gameplay_exited(self: RendererApp, _: str, payload: dict[str, Any]) -> None:  # noqa: ARG002 - future use
        self.renderer.should_exit = True
        self.renderer.current_state = RendererState.MAIN_MENU
        self._transition_to_state(RendererState.MAIN_MENU)

    def _transition_to_state(self: RendererApp, target_state: RendererState) -> None:
        if self.current_window is None:
            return
        self.renderer.current_state = target_state
        next_view = arcade_views.reconcile_view(self.renderer, self.event_bus, self._current_view)
        self._current_view = next_view
        self.current_window.show_view(next_view)


def create_renderer_app(
    *,
    renderer: HexaRenderer | None = None,
    event_bus: EventBus | None = None,
    width: int = 1280,
    height: int = 720,
    title: str = "Hexa-Core Command",
    update_rate: float | None = 1 / 60,
    window_factory: WindowFactory | None = None,
) -> RendererApp:
    base_renderer = renderer or HexaRenderer()
    bus = event_bus or EventBus()
    return RendererApp(
        renderer=base_renderer,
        event_bus=bus,
        width=width,
        height=height,
        window_title=title,
        update_rate=update_rate,
        window_factory=window_factory,
    )


def main() -> None:  # pragma: no cover - thin runtime wrapper
    app = create_renderer_app()
    app.launch()


if __name__ == "__main__":  # pragma: no cover
    main()
