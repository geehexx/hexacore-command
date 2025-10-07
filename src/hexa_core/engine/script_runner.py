"""Hexa-Script runner stub using SLY."""

from __future__ import annotations


class ScriptRunner:
    """Placeholder for the Hexa-Script execution engine."""

    def __init__(self) -> None:
        # TODO: Initialize lexer and parser built with SLY.
        self._program = None

    def load(self, source: str) -> None:
        """Load Hexa-Script source code."""
        # TODO: Parse the source into an executable form.
        self._program = source

    def execute(self, context: dict[str, object]) -> None:  # pragma: no cover - stub
        """Execute the loaded program against the provided context."""
        if self._program is None:
            raise RuntimeError("No script loaded")
        # TODO: Evaluate parsed instructions.
        raise NotImplementedError("Script execution not yet implemented")
