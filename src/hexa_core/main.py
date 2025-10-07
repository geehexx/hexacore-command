"""Entry point for Hexa-Core Command."""

from hexa_core.renderer.renderer import HexaRenderer


def main() -> None:
    """Launch the Hexa-Core Command application."""
    # Placeholder: launch renderer once engine bootstrap is implemented.
    renderer = HexaRenderer()
    renderer.run()


if __name__ == "__main__":  # pragma: no cover
    main()
