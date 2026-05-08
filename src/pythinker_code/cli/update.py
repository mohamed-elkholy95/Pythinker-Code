from __future__ import annotations

import asyncio
from typing import Annotated

import typer

cli = typer.Typer(help="Check for and install Pythinker CLI updates.")


@cli.callback(invoke_without_command=True)
def update(
    check_only: Annotated[
        bool,
        typer.Option(
            "--check",
            help="Only check whether an update is available; don't install.",
        ),
    ] = False,
):
    """Check for and install Pythinker CLI updates."""
    from pythinker_code.ui.shell.update import UpdateResult, do_update

    result = asyncio.run(do_update(print=True, check_only=check_only))
    if result in (UpdateResult.FAILED, UpdateResult.UNSUPPORTED):
        raise typer.Exit(1)
