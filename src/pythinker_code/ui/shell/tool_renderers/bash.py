"""Pi-style renderer for Pythinker's ``Shell`` tool.

Mirrors ``packages/coding-agent/src/core/tools/bash.ts`` (Pi reference).

Pi tool name → Pythinker tool name: ``bash`` → ``Shell``.
Param mapping: Pythinker has ``command``, ``timeout``, ``run_in_background``,
``description``; Pi has ``command``, ``timeout`` only.

The richer bordered "shell mode" presentation lives in
:mod:`pythinker_code.ui.shell.components.bash_execution` — for *tool*
invocations Pi keeps things compact, so we follow suit and let the
``ToolExecutionComponent`` handle the success/error background tint.
"""

from __future__ import annotations

from rich.console import Group, RenderableType
from rich.style import Style as RichStyle
from rich.text import Text

from pythinker_code.ui.shell.tool_renderers import (
    ToolRenderContext,
    ToolRenderDefinition,
    ToolResultPayload,
)
from pythinker_code.ui.shell.tool_renderers._render_utils import (
    as_str,
    fg,
    format_lines_block,
    invalid_arg,
)
from pythinker_code.ui.theme import tui_rich_style

_TOOL_NAME = "Shell"
_DEFAULT_COLLAPSED_LINES = 20


def _render_call(ctx: ToolRenderContext) -> RenderableType:
    args = ctx.args or {}
    command = as_str(args.get("command"))
    timeout = args.get("timeout")
    run_in_background = bool(args.get("run_in_background"))

    bash_mode = tui_rich_style("bash_mode")
    line = Text("$ ", style=bash_mode + RichStyle(bold=True))
    if command is None:
        if "command" in args:
            line.append_text(invalid_arg())
        else:
            line.append_text(fg("tool_output", "..."))
    else:
        line.append(command, style=bash_mode + RichStyle(bold=True))

    if isinstance(timeout, int) and timeout != 60:
        line.append_text(fg("muted", f" (timeout {timeout}s)"))
    if run_in_background:
        description = as_str(args.get("description"))
        suffix = f" (background: {description})" if description else " (background)"
        line.append_text(fg("muted", suffix))
    return line


def _render_result(ctx: ToolRenderContext, result: ToolResultPayload) -> RenderableType | None:
    if not result.text:
        return None
    body, remaining = format_lines_block(
        result.text,
        expanded=ctx.expanded,
        collapsed_max_lines=_DEFAULT_COLLAPSED_LINES,
        style_token="error" if result.is_error else "tool_output",
    )
    if not body.plain:
        return None
    if remaining > 0:
        # Pi shows "earlier lines" because bash tool truncates from the head
        # (last lines are what matter for command output).
        more = fg("muted", f"... ({remaining} earlier lines, ctrl+e to expand)")
        return Group(more, body)
    return body


SHELL_RENDERER = ToolRenderDefinition(
    name=_TOOL_NAME,
    label="bash",
    render_shell="default",
    render_call=_render_call,
    render_result=_render_result,
)
