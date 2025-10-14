"""Entry point for Hexa-Core Command."""

from hexa_core.renderer.app import create_renderer_app


def main() -> None:
    """Launch the Hexa-Core Command application."""
    app = create_renderer_app()
    app.launch()


if __name__ == "__main__":  # pragma: no cover
    main()
