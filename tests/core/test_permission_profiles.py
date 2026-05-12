from __future__ import annotations

import platform

import pytest
from pythinker_host.path import HostPath

from pythinker_code.soul.agent import Runtime
from pythinker_code.soul.approval import Approval
from pythinker_code.tools.file.write import Params as WriteParams
from pythinker_code.tools.file.write import WriteFile
from pythinker_code.tools.shell import Params as ShellParams
from pythinker_code.tools.shell import Shell
from pythinker_code.utils.environment import Environment
from tests.conftest import tool_call_context


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Shell mutation guard examples use POSIX"
)
async def test_explore_profile_denies_mutating_shell_before_approval(
    runtime: Runtime,
    environment: Environment,
    temp_work_dir: HostPath,
) -> None:
    runtime.role = "subagent"
    runtime.subagent_type = "explore"
    target = temp_work_dir / "should-not-exist.txt"

    with tool_call_context("Shell"):
        shell = Shell(Approval(yolo=True), environment, runtime)
        result = await shell(ShellParams(command=f"touch {target}"))

    assert result.is_error
    assert "permission profile blocks" in result.message
    assert not await target.exists()


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Shell mutation guard examples use POSIX"
)
@pytest.mark.parametrize("subagent_type", ["review", "verifier"])
async def test_review_and_verifier_profiles_deny_mutating_shell(
    runtime: Runtime,
    environment: Environment,
    temp_work_dir: HostPath,
    subagent_type: str,
) -> None:
    runtime.role = "subagent"
    runtime.subagent_type = subagent_type
    target = temp_work_dir / f"{subagent_type}-should-not-exist.txt"

    with tool_call_context("Shell"):
        shell = Shell(Approval(yolo=True), environment, runtime)
        result = await shell(ShellParams(command=f"echo hi > {target}"))

    assert result.is_error
    assert "output redirection" in result.message
    assert not await target.exists()


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Shell mutation guard examples use POSIX"
)
async def test_implementer_profile_allows_mutating_shell_with_approval(
    runtime: Runtime,
    environment: Environment,
    temp_work_dir: HostPath,
) -> None:
    runtime.role = "subagent"
    runtime.subagent_type = "implementer"
    target = temp_work_dir / "created-by-implementer.txt"

    with tool_call_context("Shell"):
        shell = Shell(Approval(yolo=True), environment, runtime)
        result = await shell(ShellParams(command=f"touch {target}"))

    assert not result.is_error
    assert await target.exists()


async def test_read_only_profile_denies_write_file_even_if_tool_is_present(
    runtime: Runtime,
    temp_work_dir: HostPath,
) -> None:
    runtime.role = "subagent"
    runtime.subagent_type = "explore"
    target = temp_work_dir / "write-denied.txt"

    with tool_call_context("WriteFile"):
        tool = WriteFile(runtime, Approval(yolo=True))
        result = await tool(WriteParams(path=str(target), content="nope"))

    assert result.is_error
    assert "permission profile blocks file mutations" in result.message
    assert not await target.exists()
