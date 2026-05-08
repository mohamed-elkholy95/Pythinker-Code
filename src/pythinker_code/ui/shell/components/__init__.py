"""Pi-style TUI component foundation.

This package provides reusable rendering primitives modeled after the
``@earendil-works/pi-tui`` component system. Components are pure
data-to-Rich-renderable adapters with no event-loop knowledge.
"""

from __future__ import annotations

from pythinker_code.ui.shell.components.base import TuiComponent
from pythinker_code.ui.shell.components.bash_execution import (
    BashExecutionState,
    render_bash_execution,
)
from pythinker_code.ui.shell.components.diff import (
    EditDiffResult,
    compute_edit_diff_string,
    render_diff,
)
from pythinker_code.ui.shell.components.key_hints import key_hint, raw_key_hint
from pythinker_code.ui.shell.components.render_utils import (
    cell_width,
    dim,
    render_plain,
    sanitize_ansi,
    truncate_to_width,
)
from pythinker_code.ui.shell.components.tool_execution import (
    ToolExecutionComponent,
    ToolExecutionStatus,
)

__all__ = [
    "BashExecutionState",
    "EditDiffResult",
    "ToolExecutionComponent",
    "ToolExecutionStatus",
    "TuiComponent",
    "cell_width",
    "compute_edit_diff_string",
    "dim",
    "key_hint",
    "raw_key_hint",
    "render_bash_execution",
    "render_diff",
    "render_plain",
    "sanitize_ansi",
    "truncate_to_width",
]
