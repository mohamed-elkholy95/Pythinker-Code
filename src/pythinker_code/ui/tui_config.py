"""Resolve the active TUI style from env var or loaded config.

Single accessor used by call sites to decide between the existing
``pythinker`` rendering path and the in-progress ``pi`` style. Keeps the
flag-resolution logic in one place so the migration's escape hatch can be
removed cleanly once the Pi style stabilizes.
"""

from __future__ import annotations

import os
from typing import Literal

TUIStyle = Literal["pythinker", "pi"]

_ENV_VAR = "PYTHINKER_TUI_STYLE"
_VALID: frozenset[str] = frozenset(("pythinker", "pi"))

_active_tui_style: TUIStyle = "pythinker"
"""Process-level active style. Set at shell startup from ``Config.tui.style``;
used as the fallback when neither env var nor a per-call ``configured`` value
is provided."""


def _from_env() -> TUIStyle | None:
    """Read the env var override. Returns None when unset or invalid."""
    raw = os.environ.get(_ENV_VAR)
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in _VALID:
        return value  # type: ignore[return-value]
    return None


def set_active_tui_style(style: TUIStyle | str | None) -> None:
    """Set the process-level active style.

    Called once at shell startup from the loaded config. Invalid or None
    values fall back to ``"pythinker"`` so a stale config can't break the
    shell.
    """
    global _active_tui_style
    _active_tui_style = style if style in _VALID else "pythinker"  # type: ignore[assignment]


def get_active_tui_style() -> TUIStyle:
    """Return the process-level active style (without env override)."""
    return _active_tui_style


def get_tui_style(configured: TUIStyle | str | None = None) -> TUIStyle:
    """Return the effective TUI style.

    Resolution order (first match wins):
      1. ``PYTHINKER_TUI_STYLE`` env var, if set to a valid value
      2. *configured* argument (when provided and valid)
      3. Process-level active style set via :func:`set_active_tui_style`
      4. ``"pythinker"`` (initial default)

    Unrecognized values fall through to the next layer rather than raising,
    so a stale env var or older config can't break the shell.
    """
    env = _from_env()
    if env is not None:
        return env
    if configured in _VALID:
        return configured  # type: ignore[return-value]
    return _active_tui_style


def is_pi_style(configured: TUIStyle | str | None = None) -> bool:
    """Convenience predicate for ``get_tui_style(...) == "pi"``."""
    return get_tui_style(configured) == "pi"
