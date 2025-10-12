"""HexaRenderer specifications."""

from __future__ import annotations

# ruff: noqa: S101
from hexa_core.renderer.renderer import HexaRenderer, MenuOption, RendererState


def describe_hexa_renderer() -> None:
    def it_defaults_to_main_menu_state() -> None:
        renderer = HexaRenderer()

        assert renderer.current_state is RendererState.MAIN_MENU

        main_menu = renderer.build_main_menu()
        assert main_menu.title == "Hexa-Core Command"
        assert [option.action for option in main_menu.options] == [
            "start_new_game",
            "level_select",
            "options",
            "exit",
        ]
        enabled_options = [option.action for option in main_menu.options if option.enabled]
        assert enabled_options == ["start_new_game", "exit"]

    def it_transitions_to_mission_briefing_when_starting_new_game() -> None:
        renderer = HexaRenderer()

        renderer.select_menu_option("start_new_game")

        assert renderer.current_state is RendererState.MISSION_BRIEFING

    def it_sets_exit_flag_when_exit_option_selected() -> None:
        renderer = HexaRenderer()

        renderer.select_menu_option("exit")

        assert renderer.should_exit is True
        assert renderer.current_state is RendererState.MAIN_MENU

    def it_builds_mission_briefing_from_map_payload() -> None:
        renderer = HexaRenderer()

        renderer.load_mission_briefing(
            {
                "name": "Operation Dawn",
                "objectives": ["Secure landing zone", "Extract scout team"],
                "grid_size": {"width": 12, "height": 10},
            }
        )

        assert renderer.current_state is RendererState.MISSION_BRIEFING
        briefing = renderer.mission_briefing
        assert briefing is not None
        assert briefing.title == "Operation Dawn"
        assert briefing.objectives == (
            "Secure landing zone",
            "Extract scout team",
        )
        assert briefing.grid_size == (12, 10)

    def it_transitions_to_gameplay_after_briefing() -> None:
        renderer = HexaRenderer()
        renderer.load_mission_briefing(
            {
                "name": "Operation Dawn",
                "objectives": [],
                "grid_size": {"width": 12, "height": 10},
            }
        )

        renderer.proceed_to_gameplay()

        assert renderer.should_exit is False
        assert renderer.current_state is RendererState.GAMEPLAY
        assert renderer.mission_briefing is None

    def it_formats_mission_briefing_for_display() -> None:
        renderer = HexaRenderer()

        renderer.load_mission_briefing(
            {
                "name": "Operation Dawn",
                "objectives": [
                    "Secure landing zone",
                    "Extract scout team",
                ],
                "grid_size": {"width": 12, "height": 10},
            }
        )

        briefing = renderer.mission_briefing
        assert briefing is not None
        assert briefing.objective_lines == (
            "1. Secure landing zone",
            "2. Extract scout team",
        )
        assert briefing.grid_summary == "Grid: 12 × 10"


def describe_menu_option() -> None:
    def it_exposes_menu_option_properties() -> None:
        option = MenuOption(label="Start New Game", action="start_new_game", enabled=True)

        assert option.label == "Start New Game"
        assert option.action == "start_new_game"
        assert option.enabled is True
