from __future__ import annotations

import asyncio
import re
import shlex
import subprocess
import sys
from enum import Enum, auto

import aiohttp

from pythinker_code.share import get_share_dir
from pythinker_code.ui.shell.console import console
from pythinker_code.utils.aiohttp import new_client_session
from pythinker_code.utils.logging import logger

PYPI_JSON_URL = "https://pypi.org/pypi/pythinker-code/json"
CHANGELOG_URL_EN = "https://github.com/mohamed-elkholy95/Pythinker-Code/blob/main/CHANGELOG.md"

# Default upgrade command. `_detect_upgrade_command()` overrides this when the
# install method is recognizable from `sys.executable`.
UPGRADE_COMMAND = "uv tool upgrade pythinker-code"

LATEST_VERSION_FILE = get_share_dir() / "latest_version.txt"
SKIPPED_VERSION_FILE = get_share_dir() / "skipped_version.txt"

_UPDATE_LOCK = asyncio.Lock()


class UpdateResult(Enum):
    UPDATE_AVAILABLE = auto()
    UPDATED = auto()
    UP_TO_DATE = auto()
    FAILED = auto()
    UNSUPPORTED = auto()


def semver_tuple(version: str) -> tuple[int, int, int]:
    v = version.strip()
    if v.startswith("v"):
        v = v[1:]
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?", v)
    if not match:
        return (0, 0, 0)
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3) or 0)
    return (major, minor, patch)


def _detect_upgrade_command() -> str:
    """Pick the right upgrade command based on how this interpreter was installed."""
    exe = sys.executable.replace("\\", "/").lower()
    if "/uv/tools/" in exe:
        return "uv tool upgrade pythinker-code"
    if "/pipx/venvs/" in exe:
        return "pipx upgrade pythinker-code"
    return f"{sys.executable} -m pip install --upgrade pythinker-code"


async def _get_latest_version(session: aiohttp.ClientSession) -> str | None:
    try:
        async with session.get(PYPI_JSON_URL) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
            version = data.get("info", {}).get("version")
            return str(version).strip() if version else None
    except (TimeoutError, aiohttp.ClientError):
        logger.exception("Failed to fetch latest version from PyPI:")
        return None
    except Exception:
        logger.exception("Failed to parse PyPI response:")
        return None


def print_update_banner() -> None:
    """Print a non-blocking 'Update Available' banner if a newer version is cached."""
    from pythinker_code.constant import VERSION as current_version
    from pythinker_code.utils.envvar import get_env_bool

    if get_env_bool("PYTHINKER_CLI_NO_AUTO_UPDATE"):
        return
    if not sys.stdout.isatty():
        return
    if not LATEST_VERSION_FILE.exists():
        return

    try:
        latest_version = LATEST_VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return
    if not latest_version or semver_tuple(latest_version) <= semver_tuple(current_version):
        return

    if SKIPPED_VERSION_FILE.exists():
        try:
            skipped = SKIPPED_VERSION_FILE.read_text(encoding="utf-8").strip()
        except OSError:
            skipped = ""
        if skipped == latest_version:
            return

    _render_update_banner(current_version, latest_version)


def _render_update_banner(current_version: str, latest_version: str) -> None:
    from rich.panel import Panel
    from rich.text import Text

    upgrade_command = _detect_upgrade_command()
    body = Text.assemble(
        ("New version ", ""),
        (latest_version, "bold green"),
        (" is available", ""),
        (f" (current: {current_version}).", "grey50"),
        ("\nRun ", ""),
        ("pythinker update", "bold cyan"),
        (" or: ", ""),
        (upgrade_command, "bold"),
        ("\nChangelog: ", "grey50"),
        (CHANGELOG_URL_EN, "dodger_blue1"),
    )
    console.print()
    console.print(
        Panel(
            body,
            title="[bold yellow]Update Available[/bold yellow]",
            border_style="yellow",
            expand=False,
            padding=(0, 2),
        )
    )


async def do_update(*, print: bool = True, check_only: bool = False) -> UpdateResult:
    async with _UPDATE_LOCK:
        return await _do_update(print=print, check_only=check_only)


async def _do_update(*, print: bool, check_only: bool) -> UpdateResult:
    from pythinker_code.constant import VERSION as current_version

    def _print(message: str) -> None:
        if print:
            console.print(message)

    timeout = aiohttp.ClientTimeout(total=15, sock_connect=5, sock_read=10)
    async with new_client_session(timeout=timeout) as session:
        logger.info("Checking for updates...")
        _print("Checking for updates...")
        latest_version = await _get_latest_version(session)
        if not latest_version:
            _print("[red]Failed to check for updates.[/red]")
            return UpdateResult.FAILED

    logger.debug("Latest version: {latest_version}", latest_version=latest_version)
    try:
        LATEST_VERSION_FILE.write_text(latest_version, encoding="utf-8")
    except OSError:
        logger.exception("Failed to cache latest version:")

    if semver_tuple(current_version) >= semver_tuple(latest_version):
        logger.debug("Already up to date: {current_version}", current_version=current_version)
        _print("[green]Already up to date.[/green]")
        return UpdateResult.UP_TO_DATE

    if check_only:
        logger.info(
            "Update available: current={current_version}, latest={latest_version}",
            current_version=current_version,
            latest_version=latest_version,
        )
        _print(f"[yellow]Update available: {latest_version}[/yellow]")
        return UpdateResult.UPDATE_AVAILABLE

    upgrade_command = _detect_upgrade_command()
    logger.info(
        "Updating from {current_version} to {latest_version} via: {cmd}",
        current_version=current_version,
        latest_version=latest_version,
        cmd=upgrade_command,
    )
    _print(f"Updating pythinker-code {current_version} → {latest_version}...")
    _print(f"[grey50]Running: {upgrade_command}[/grey50]")
    try:
        result = subprocess.run(shlex.split(upgrade_command))
    except OSError as e:
        logger.exception("Upgrade failed:")
        _print(f"[red]Upgrade failed:[/red] {e}")
        _print(f"Please run manually: {upgrade_command}")
        return UpdateResult.FAILED

    if result.returncode == 0:
        _print("[green]Updated successfully![/green]")
        _print("[yellow]Restart Pythinker CLI to use the new version.[/yellow]")
        return UpdateResult.UPDATED
    _print("[red]Upgrade failed. Please try running manually:[/red]")
    _print(f"  {upgrade_command}")
    return UpdateResult.FAILED
