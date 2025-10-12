"""Arcade renderer placeholder for Hexa-Core Command."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
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
class ObjectiveBlock:
    heading: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class MapPreviewInfo:
    asset_path: str
    dimensions: tuple[int, int]
    alt_text: str


@dataclass(frozen=True)
class InteractionCues:
    primary: str
    secondary: str
    hints: tuple[str, ...]

    @staticmethod
    def default() -> InteractionCues:
        return InteractionCues("", "", ())


@dataclass(frozen=True)
class MainMenuView:
    title: str
    options: tuple[MenuOption, ...]


@dataclass(frozen=True)
class MissionBriefingView:
    title: str
    objectives: tuple[str, ...]
    grid_size: tuple[int, int]
    map_preview: MapPreviewInfo | None = None
    interaction_cues: InteractionCues = field(default_factory=InteractionCues.default)

    @property
    def objective_lines(self: MissionBriefingView) -> tuple[str, ...]:
        return tuple(f"{index}. {objective}" for index, objective in enumerate(self.objectives, start=1))

    @property
    def grid_summary(self: MissionBriefingView) -> str:
        width, height = self.grid_size
        return f"Grid: {width} × {height}"

    def objective_blocks(self: MissionBriefingView, max_width: int) -> tuple[ObjectiveBlock, ...]:
        width = max(1, max_width)
        blocks: list[ObjectiveBlock] = []
        for index, raw_objective in enumerate(self.objectives, start=1):
            text = raw_objective.strip()
            lines = self._wrap_objective(text, width)
            blocks.append(ObjectiveBlock(heading=f"Objective {index}", lines=lines))
        return tuple(blocks)

    @staticmethod
    def _wrap_objective(text: str, width: int) -> tuple[str, ...]:
        if not text:
            return ()
        words = text.split()
        if not words:
            return ()
        chunks = MissionBriefingView._collect_chunks(words, width)
        MissionBriefingView._rebalance_chunks(chunks, width)
        return tuple(" ".join(chunk) for chunk in chunks)

    @staticmethod
    def _collect_chunks(words: list[str], width: int) -> list[list[str]]:
        chunks: list[list[str]] = []
        current: list[str] = []
        current_length = 0
        for word in words:
            if not current:
                current = [word]
                current_length = len(word)
                continue
            next_length = current_length + 1 + len(word)
            if len(word) >= width or next_length > width:
                chunks.append(current)
                current = [word]
                current_length = len(word)
            else:
                current.append(word)
                current_length = next_length
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _rebalance_chunks(chunks: list[list[str]], width: int) -> None:
        if len(chunks) < 2:
            return
        min_length = max(1, width // 2 - 1)
        while len(chunks) >= 2 and MissionBriefingView._joined_length(chunks[-1]) < min_length:
            donor_index = len(chunks) - 2
            donor = chunks[donor_index]
            if len(donor) <= 1:
                break
            recipient = chunks[-1]
            recipient.insert(0, donor.pop())
            if not donor:
                chunks.pop(donor_index)

    @staticmethod
    def _joined_length(words: list[str]) -> int:
        if not words:
            return 0
        return sum(len(word) for word in words) + (len(words) - 1)


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
        preview_section = payload.get("preview", {})
        preview: MapPreviewInfo | None = None
        if isinstance(preview_section, dict):
            asset_path = str(preview_section.get("image", ""))
            preview_width = int(preview_section.get("width", 0))
            preview_height = int(preview_section.get("height", 0))
            alt_text = str(preview_section.get("alt_text", ""))
            if asset_path:
                preview = MapPreviewInfo(asset_path, (preview_width, preview_height), alt_text)
        interaction_section = payload.get("interaction", {})
        cues = InteractionCues.default()
        if isinstance(interaction_section, dict):
            primary = str(interaction_section.get("primary", ""))
            secondary = str(interaction_section.get("secondary", ""))
            hints_raw = interaction_section.get("hints", ())
            hints_iter = (
                hints_raw
                if isinstance(hints_raw, Iterable) and not isinstance(hints_raw, str | bytes)
                else ()
            )
            hints = tuple(str(item) for item in hints_iter)
            cues = InteractionCues(primary=primary, secondary=secondary, hints=hints)
        self.mission_briefing = MissionBriefingView(
            name,
            objectives,
            (width, height),
            map_preview=preview,
            interaction_cues=cues,
        )
        self.current_state = RendererState.MISSION_BRIEFING
        self.should_exit = False

    def proceed_to_gameplay(self: HexaRenderer) -> None:
        self.mission_briefing = None
        self.current_state = RendererState.GAMEPLAY
        self.should_exit = False
