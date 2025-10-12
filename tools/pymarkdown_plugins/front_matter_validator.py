"""Custom PyMarkdown plugin validating Windsurf rule/workflow front matter."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymarkdown.extensions.front_matter_markdown_token import (
    FrontMatterMarkdownToken,
)
from pymarkdown.plugin_manager.plugin_details import PluginDetailsV2
from pymarkdown.plugin_manager.plugin_scan_context import PluginScanContext
from pymarkdown.plugin_manager.rule_plugin import RulePlugin
from pymarkdown.tokens.markdown_token import MarkdownToken

WORKFLOW_NAME_PATTERN = re.compile(r"^[\w\d _-]+$")


@dataclass(frozen=True)
class _ValidationConfig:
    description_min_length: int
    require_auto_execution_mode: bool


class WindsurfFrontMatterValidator(RulePlugin):
    """Ensures Windsurf rule/workflow documents declare valid front matter."""

    _WORKFLOW_CONFIG = _ValidationConfig(
        description_min_length=15,
        require_auto_execution_mode=True,
    )
    _RULE_CONFIG = _ValidationConfig(
        description_min_length=25,
        require_auto_execution_mode=False,
    )

    def __init__(self: Self) -> None:
        super().__init__()
        self._category: str | None = None
        self._scan_path: Path | None = None
        self._front_matter_seen = False

    def get_details(self: Self) -> PluginDetailsV2:
        return PluginDetailsV2(
            plugin_name="windsurf-front-matter",
            plugin_id="PML300",
            plugin_enabled_by_default=True,
            plugin_description="Validate Windsurf workflow/rule front matter",
            plugin_version="0.1.0",
            plugin_interface_version=2,
        )

    def starting_new_file(self: Self) -> None:
        self._category = None
        self._scan_path = None
        self._front_matter_seen = False

    def completed_file(self: Self, context: PluginScanContext) -> None:
        if self._category is None:
            return
        if not self._front_matter_seen:
            self._report_error(
                context,
                line_number=1,
                column_number=1,
                message="Front matter header (`---`) is required for Windsurf documents.",
            )

    def next_token(
        self: Self, context: PluginScanContext, token: MarkdownToken
    ) -> None:
        if self._category is None:
            self._initialize_category(context.scan_file)

        if self._category is None:
            return

        if token.is_front_matter:
            self._front_matter_seen = True
            self._validate_front_matter(context, token)

    def _initialize_category(self: Self, raw_path: str) -> None:
        candidate = Path(raw_path)
        normalized = Path("/").joinpath(*candidate.parts).as_posix()
        if "/.windsurf/workflows/" in normalized:
            self._category = "workflow"
        elif "/.windsurf/rules/" in normalized:
            self._category = "rule"
        else:
            self._category = None

        if self._category is not None:
            self._scan_path = candidate

    def _validate_front_matter(
        self: Self, context: PluginScanContext, token: MarkdownToken
    ) -> None:
        front_token = self._as_front_matter(token)
        mapping = {
            str(key): str(value)
            for key, value in front_token.matter_map.items()
        }

        if self._category == "workflow":
            self._validate_workflow(context, front_token, mapping)
        elif self._category == "rule":
            self._validate_rule(context, front_token, mapping)

    @staticmethod
    def _as_front_matter(token: MarkdownToken) -> FrontMatterMarkdownToken:
        if not isinstance(token, FrontMatterMarkdownToken):
            raise TypeError("Front matter token expected")
        return token

    def _validate_workflow(
        self: Self,
        context: PluginScanContext,
        token: FrontMatterMarkdownToken,
        mapping: dict[str, str],
    ) -> None:
        errors = []
        errors.extend(
            self._validate_description(mapping, self._WORKFLOW_CONFIG)
        )
        errors.extend(self._validate_auto_execution_mode(mapping))
        errors.extend(self._validate_workflow_filename())
        self._emit_errors(context, token, errors)

    def _validate_rule(
        self: Self,
        context: PluginScanContext,
        token: FrontMatterMarkdownToken,
        mapping: dict[str, str],
    ) -> None:
        errors = []
        errors.extend(self._validate_description(mapping, self._RULE_CONFIG))
        if "auto_execution_mode" in mapping:
            errors.append("Rules MUST NOT define `auto_execution_mode`.")
        self._emit_errors(context, token, errors)

    def _emit_errors(
        self: Self,
        context: PluginScanContext,
        token: MarkdownToken,
        errors: Iterable[str],
    ) -> None:
        for error in errors:
            self.report_next_token_error(context, token, extra_error_information=error)

    def _report_error(
        self: Self,
        context: PluginScanContext,
        line_number: int,
        column_number: int,
        message: str,
    ) -> None:
        details = self.get_details()
        context.add_triggered_rule(
            context.scan_file,
            line_number,
            column_number,
            details.plugin_id,
            details.plugin_name,
            details.plugin_description,
            message,
            details.plugin_supports_fix,
        )

    def _validate_description(
        self: Self,
        mapping: dict[str, str],
        config: _ValidationConfig,
    ) -> list[str]:
        description = mapping.get("description", "").strip()
        if not description:
            return ["`description` is required in front matter."]
        if len(description) < config.description_min_length:
            return [
                "`description` must be at least "
                f"{config.description_min_length} characters long.",
            ]
        return []

    def _validate_auto_execution_mode(self: Self, mapping: dict[str, str]) -> list[str]:
        mode_raw = mapping.get("auto_execution_mode")
        if mode_raw is None:
            return ["`auto_execution_mode` must be declared for workflows."]

        try:
            mode_value = int(mode_raw.strip())
        except ValueError:
            return ["`auto_execution_mode` must be an integer (2 or 3)."]

        if mode_value not in {2, 3}:
            return ["`auto_execution_mode` must be set to 2 or 3."]
        return []

    def _validate_workflow_filename(self: Self) -> list[str]:
        if self._scan_path is None:
            return []

        errors: list[str] = []
        stem = self._scan_path.stem
        if len(stem) < 4:
            errors.append("Workflow file name must be at least 4 characters long.")
        if not WORKFLOW_NAME_PATTERN.fullmatch(stem):
            errors.append(
                "Workflow file name must match the pattern `^[\\w\\d _-]+$`."
            )
        return errors
