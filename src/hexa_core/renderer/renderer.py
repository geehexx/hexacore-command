"""Arcade renderer placeholder for Hexa-Core Command."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
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


@dataclass(frozen=True)
class ControlButton:
    label: str
    action: str
    enabled: bool = True


@dataclass(frozen=True)
class BotStatusEntry:
    label: str
    value: str


@dataclass(frozen=True)
class BotStatusPanel:
    heading: str
    entries: tuple[BotStatusEntry, ...]


@dataclass(frozen=True)
class ScriptEditorView:
    title: str
    content: str
    language: str
    read_only: bool = False


@dataclass(frozen=True)
class GridPanelView:
    title: str
    dimensions: tuple[int, int]
    preview: MapPreviewInfo | None = None


@dataclass(frozen=True)
class GameplayView:
    grid_panel: GridPanelView
    script_editor: ScriptEditorView
    bot_status: BotStatusPanel
    controls: tuple[ControlButton, ...]


class HexaRenderer:
    """Renderer state machine decoupled from Arcade runtime."""

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
        self.gameplay_view: GameplayView | None = None

    def run(self: HexaRenderer) -> None:
        """Execute the render loop."""
        raise RuntimeError("HexaRenderer.run() is managed by RendererApp")

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
        self.mission_briefing = self._create_mission_briefing_view(payload)
        self.current_state = RendererState.MISSION_BRIEFING
        self.should_exit = False

    def proceed_to_gameplay(self: HexaRenderer) -> None:
        if self.mission_briefing is None:
            raise ValueError("Mission briefing not loaded")
        self.gameplay_view = self.build_gameplay_view(self.mission_briefing)
        self.mission_briefing = None
        self.current_state = RendererState.GAMEPLAY
        self.should_exit = False

    def build_gameplay_view(self: HexaRenderer, briefing: MissionBriefingView | None = None) -> GameplayView:
        source = briefing or self.mission_briefing
        title = "Simulation"
        grid_size = (0, 0)
        preview: MapPreviewInfo | None = None
        if source is not None:
            title = source.title
            grid_size = source.grid_size
            preview = source.map_preview
        grid_panel = GridPanelView(title=title, dimensions=grid_size, preview=preview)
        script_editor = ScriptEditorView(
            title="Hexa-Script Editor",
            content="",
            language="hexascript",
            read_only=False,
        )
        bot_status = BotStatusPanel(heading="Bot Status", entries=())
        controls = (
            ControlButton("Deploy Script", "deploy_script", True),
            ControlButton("Pause Simulation", "pause_simulation", True),
            ControlButton("Reset Level", "reset_level", True),
        )
        return GameplayView(
            grid_panel=grid_panel,
            script_editor=script_editor,
            bot_status=bot_status,
            controls=controls,
        )

    def _create_mission_briefing_view(self: HexaRenderer, payload: Mapping[str, object]) -> MissionBriefingView:
        name = str(payload.get("name", ""))
        objectives = self._coerce_string_iterable(payload.get("objectives"))
        grid_size = self._parse_grid(payload.get("grid_size"))
        preview = self._parse_preview(payload.get("preview"))
        interaction_cues = self._parse_interaction(payload.get("interaction"))
        return MissionBriefingView(
            name,
            objectives,
            grid_size,
            map_preview=preview,
            interaction_cues=interaction_cues,
        )

    @staticmethod
    def _coerce_string_iterable(value: object) -> tuple[str, ...]:
        if isinstance(value, Iterable) and not isinstance(value, str | bytes):
            return tuple(str(item) for item in value)
        return ()

    @staticmethod
    def _parse_grid(section: object) -> tuple[int, int]:
        if isinstance(section, Mapping):
            width = int(section.get("width", 0))
            height = int(section.get("height", 0))
            return width, height
        return 0, 0

    @staticmethod
    def _parse_preview(section: object) -> MapPreviewInfo | None:
        if not isinstance(section, Mapping):
            return None
        asset_path = str(section.get("image", ""))
        if not asset_path:
            return None
        preview_width = int(section.get("width", 0))
        preview_height = int(section.get("height", 0))
        alt_text = str(section.get("alt_text", ""))
        return MapPreviewInfo(asset_path, (preview_width, preview_height), alt_text)

    def _parse_interaction(self: HexaRenderer, section: object) -> InteractionCues:
        if not isinstance(section, Mapping):
            return InteractionCues.default()
        primary = str(section.get("primary", ""))
        secondary = str(section.get("secondary", ""))
        hints = self._coerce_string_iterable(section.get("hints"))
        return InteractionCues(primary=primary, secondary=secondary, hints=hints)
