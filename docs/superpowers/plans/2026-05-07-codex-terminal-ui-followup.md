# Codex Terminal UI Follow-Up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply a Codex-style visual pass to the prompt input, slash command menu, subagent activity rows, and diff summaries.

**Architecture:** Keep the existing prompt-toolkit and Rich renderers. Tune prompt-toolkit window sizing/layout for the composer and slash popup, and make focused Rich renderer changes for worklog/subagent/diff cards.

**Tech Stack:** Python, prompt-toolkit, Rich, pytest.

---

### Task 1: Prompt Composer Growth

**Files:**
- Modify: `src/pythinker_code/ui/shell/prompt.py`
- Test: `tests/ui_and_conv/test_prompt_tips.py`

- [ ] **Step 1: Write failing tests**

Assert the prompt buffer has `preferred == 2` and `max == 5`, keeps compact input styling, and slash menu remains directly below the prompt buffer.

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run pytest tests/ui_and_conv/test_prompt_tips.py::test_prompt_buffer_window_grows_to_five_visible_rows -q`

Expected: FAIL because current max is 2.

- [ ] **Step 3: Implement minimal prompt sizing**

Set prompt buffer height to `Dimension(preferred=2, max=5)` and keep the slash menu sibling layout below the prompt buffer.

- [ ] **Step 4: Verify prompt tests**

Run: `uv run pytest tests/ui_and_conv/test_prompt_tips.py tests/ui_and_conv/test_slash_completer.py -q`

Expected: PASS.

### Task 2: Worklog Codex Polish

**Files:**
- Modify: `src/pythinker_code/ui/shell/visualize/_worklog.py`
- Modify: `src/pythinker_code/ui/shell/visualize/_blocks.py`
- Test: `tests/ui_and_conv/test_tool_call_block.py`
- Test: `tests/ui_and_conv/test_worklog_render.py`

- [ ] **Step 1: Write failing tests**

Assert running subagents render a spinner and diff summaries include file path plus added/removed counts in compact cards.

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run pytest tests/ui_and_conv/test_tool_call_block.py tests/ui_and_conv/test_worklog_render.py -q`

Expected: FAIL for any missing Codex-style summary behavior.

- [ ] **Step 3: Implement renderer updates**

Keep spinner bullets for running subagents. Adjust diff summary rendering to be compact, grouped by file, and count-focused.

- [ ] **Step 4: Verify worklog tests**

Run: `uv run pytest tests/ui_and_conv/test_tool_call_block.py tests/ui_and_conv/test_worklog_render.py -q`

Expected: PASS.

### Task 3: Full Verification

**Files:**
- Verify all changed files.

- [ ] **Step 1: Run targeted UI tests**

Run: `uv run pytest tests/ui_and_conv/test_prompt_tips.py tests/ui_and_conv/test_slash_completer.py tests/ui_and_conv/test_tool_call_block.py tests/ui_and_conv/test_worklog_render.py tests/e2e/test_slash_completion_enter_tmux.py -q`

Expected: PASS.

- [ ] **Step 2: Run full UI suite**

Run: `uv run pytest tests/ui_and_conv -q`

Expected: PASS.

- [ ] **Step 3: Run lint/format checks**

Run: `uv run ruff check <changed files>` and `uv run ruff format --check <changed files>`.

Expected: PASS.
