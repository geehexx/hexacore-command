"""Arcade renderer placeholder for Hexa-Core Command."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto


class RendererState(Enum):
    MAIN_MENU = auto()
    MISSION_BRIEFING = auto()
    GAMEPLAY = auto()


@dataclass(frozen=True)
class MenuOption:
    label: str
    action: str
    enabled: bool = True


@dataclass(frozen=True)
class MainMenuView:
    title: str
    options: tuple[MenuOption, ...]


@dataclass(frozen=True)
class MissionBriefingView:
    title: str
    objectives: tuple[str, ...]
    grid_size: tuple[int, int]


class HexaRenderer:
    """Placeholder renderer that will eventually integrate with Arcade."""

    def __init__(self: HexaRenderer) -> None:
        self.current_state = RendererState.MAIN_MENU
        self.should_exit = False
        self._menu_view = self.build_main_menu()
        self._transitions: dict[str, RendererState] = {
            "start_new_game": RendererState.MISSION_BRIEFING,
            "level_select": RendererState.MAIN_MENU,
            "options": RendererState.MAIN_MENU,
        }
        self.mission_briefing: MissionBriefingView | None = None

    def run(self: HexaRenderer) -> None:
        """Execute the render loop."""
        # TODO: Implement Arcade window and rendering pipeline.
        raise NotImplementedError("Renderer run loop not yet implemented")

    def build_main_menu(self: HexaRenderer) -> MainMenuView:
        options = (
            MenuOption("Start New Game", "start_new_game", True),
            MenuOption("Level Select", "level_select", False),
            MenuOption("Options", "options", False),
            MenuOption("Exit", "exit", True),
        )
        return MainMenuView("Hexa-Core Command", options)

    def select_menu_option(self: HexaRenderer, action: str) -> None:
        option_map = {option.action: option for option in self._menu_view.options}
        option = option_map.get(action)
        if option is None:
            raise ValueError(f"Unknown menu action: {action}")
        if not option.enabled:
            raise ValueError(f"Menu action disabled: {action}")
        if action == "exit":
            self.should_exit = True
            self.current_state = RendererState.MAIN_MENU
            return
        self.should_exit = False
        self.current_state = self._transitions.get(action, self.current_state)

    def load_mission_briefing(self: HexaRenderer, payload: dict[str, object]) -> None:
        name = str(payload.get("name", ""))
        objectives_raw = payload.get("objectives", [])
        objectives_iter = (
            objectives_raw
            if isinstance(objectives_raw, Iterable) and not isinstance(objectives_raw, str | bytes)
            else ()
        )
        objectives = tuple(str(item) for item in objectives_iter)
        grid_section = payload.get("grid_size", {})
        width = 0
        height = 0
        if isinstance(grid_section, dict):
            width = int(grid_section.get("width", 0))
            height = int(grid_section.get("height", 0))
        self.mission_briefing = MissionBriefingView(name, objectives, (width, height))
        self.current_state = RendererState.MISSION_BRIEFING
        self.should_exit = False

    def proceed_to_gameplay(self: HexaRenderer) -> None:
        self.mission_briefing = None
        self.current_state = RendererState.GAMEPLAY
        self.should_exit = False
