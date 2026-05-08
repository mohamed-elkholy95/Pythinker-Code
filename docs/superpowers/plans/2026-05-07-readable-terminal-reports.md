# Readable Terminal Reports Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make long audit/search/report output readable in the terminal and collapse completed subagent traces into compact summaries.

**Architecture:** Add adaptive rendering at the existing Rich markdown table layer so model output does not need to change. Add completed-subagent summarization inside the existing tool-call block so running subagents keep live detail but completed ones become scannable.

**Tech Stack:** Python 3.12+, Rich renderables, markdown-it-py tokens, pytest, Ruff.

---

## File Structure

- Modify `src/pythinker_code/utils/rich/markdown.py` to render wide/long markdown tables as row cards.
- Modify `tests/utils/test_rich_markdown.py` to cover adaptive report table rendering.
- Modify `src/pythinker_code/ui/shell/visualize/_blocks.py` to summarize completed subagent child calls.
- Modify `tests/ui_and_conv/test_worklog_render.py` to cover compact completed subagent summaries.
- Keep the already-started prompt paste fix in `src/pythinker_code/ui/shell/prompt.py` and `tests/ui_and_conv/test_prompt_tips.py`.

## Task 1: Adaptive Markdown Report Tables

**Files:**
- Modify: `tests/utils/test_rich_markdown.py`
- Modify: `src/pythinker_code/utils/rich/markdown.py:280-308`

- [ ] **Step 1: Write the failing markdown table test**

Add this test to `tests/utils/test_rich_markdown.py`:

```python
def test_wide_markdown_table_renders_as_readable_records() -> None:
    console = Console(width=72, record=True, color_system=None)
    markdown = Markdown(
        "| Area | Issue | Why it matters | Suggested improvement | Priority | Effort |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| Accessibility | Search input in `web/src/components/sessions.tsx` relies on placeholder text only. | Placeholder-only labels are weak for screen readers and disappear during typing. | Add `aria-label=\"Search sessions\"` or a visually hidden label. | High | XS |\n"
    )

    console.print(markdown)
    output = console.export_text()

    assert "1. Accessibility" in output
    assert "Issue:" in output
    assert "Why it matters:" in output
    assert "Suggested improvement:" in output
    assert "Priority: High" in output
    assert "Effort: XS" in output
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `uv run pytest tests/utils/test_rich_markdown.py::test_wide_markdown_table_renders_as_readable_records -q`

Expected: FAIL because the current renderer prints a Rich table, not `1. Accessibility` records.

- [ ] **Step 3: Implement adaptive table rendering**

In `src/pythinker_code/utils/rich/markdown.py`, add helpers near `TableElement` and update `TableElement.__rich_console__`:

```python
def _cell_plain(cell: Text) -> str:
    return cell.plain.strip()


def _table_should_render_as_records(headers: list[str], rows: list[list[Text]]) -> bool:
    if len(headers) >= 4:
        return True
    return any(len(_cell_plain(cell)) > 48 for row in rows for cell in row)


def _record_title(row_index: int, headers: list[str], row: list[Text]) -> Text:
    title = _cell_plain(row[0]) if row else "Row"
    return Text(f"{row_index}. {title}", style="bold")
```

Then replace the table-only render path with:

```python
headers = [column.content.plain.strip() for column in self.header.row.cells] if self.header is not None and self.header.row is not None else []
rows = [row.cells for row in self.body.rows] if self.body is not None else []

if headers and rows and _table_should_render_as_records(headers, rows):
    for row_index, row in enumerate(rows, start=1):
        yield _record_title(row_index, headers, row)
        for header, cell in zip(headers[1:], row[1:], strict=False):
            value = _cell_plain(cell)
            if not value:
                continue
            line = Text("  ")
            line.append(f"{header}: ", style="bold")
            line.append_text(cell)
            yield line
    return
```

Keep the existing Rich table path for small tables.

- [ ] **Step 4: Run markdown tests**

Run: `uv run pytest tests/utils/test_rich_markdown.py -q`

Expected: PASS.

## Task 2: Compact Completed Subagent Summaries

**Files:**
- Modify: `tests/ui_and_conv/test_worklog_render.py`
- Modify: `src/pythinker_code/ui/shell/visualize/_blocks.py:450-478`

- [ ] **Step 1: Write the failing subagent summary test**

Add a unit test that builds a completed `ToolCallBlock` for an `Agent` tool with many finished child calls, then renders it.

The expected assertions are:

```python
assert "Subagent" in output
assert "completed" in output.lower()
assert "tool calls" in output
assert output.count("Used ReadFile") <= 3
assert "more tool" not in output.lower()
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `uv run pytest tests/ui_and_conv/test_worklog_render.py::test_completed_subagent_renders_compact_summary -q`

Expected: FAIL because completed subagents currently include the hidden-count line and individual `Used ReadFile` rows.

- [ ] **Step 3: Implement completed-only summarization**

In `_ToolCallBlock.compose`, only append full child call rows while the subagent is running. When `style.label == "Subagent"` and `self._result is not None`, replace child call rows with one summary line:

```python
if style.label == "Subagent" and self._result is not None and self._n_finished_subagent_tool_calls:
    summary = Text()
    summary.append(f"{self._n_finished_subagent_tool_calls} tool calls", style="grey50")
    if self._finished_subagent_tool_calls:
        shown = len(self._finished_subagent_tool_calls)
        summary.append(f" · {shown} recent shown", style="grey50")
    children.append(BulletColumns(summary, bullet_style="grey50"))
elif self._n_finished_subagent_tool_calls > MAX_SUBAGENT_TOOL_CALLS_TO_SHOW:
    ...
```

Preserve error display blocks and error detail.

- [ ] **Step 4: Run worklog tests**

Run: `uv run pytest tests/ui_and_conv/test_worklog_render.py -q`

Expected: PASS.

## Task 3: Finish Prompt Paste Regression

**Files:**
- Modify: `tests/ui_and_conv/test_prompt_tips.py`
- Modify: `src/pythinker_code/ui/shell/prompt.py:1644-1648`

- [ ] **Step 1: Confirm the regression test passes**

Run: `uv run pytest tests/ui_and_conv/test_prompt_tips.py::test_prompt_buffer_expands_for_long_pasted_prompt -q`

Expected: PASS after `buffer_window.height = Dimension(min=1, max=5)`.

- [ ] **Step 2: Run prompt layout tests**

Run: `uv run pytest tests/ui_and_conv/test_prompt_tips.py tests/ui_and_conv/test_slash_completer.py -q`

Expected: PASS.

## Task 4: Verification And Commit

**Files:**
- Verify all modified source and test files.

- [ ] **Step 1: Run focused tests**

Run: `uv run pytest tests/utils/test_rich_markdown.py tests/ui_and_conv/test_worklog_render.py tests/ui_and_conv/test_prompt_tips.py tests/ui_and_conv/test_slash_completer.py -q`

Expected: PASS.

- [ ] **Step 2: Run formatting and lint checks**

Run: `uv run ruff check src/pythinker_code/utils/rich/markdown.py src/pythinker_code/ui/shell/visualize/_blocks.py src/pythinker_code/ui/shell/prompt.py tests/utils/test_rich_markdown.py tests/ui_and_conv/test_worklog_render.py tests/ui_and_conv/test_prompt_tips.py`

Expected: PASS.

Run: `uv run ruff format --check src/pythinker_code/utils/rich/markdown.py src/pythinker_code/ui/shell/visualize/_blocks.py src/pythinker_code/ui/shell/prompt.py tests/utils/test_rich_markdown.py tests/ui_and_conv/test_worklog_render.py tests/ui_and_conv/test_prompt_tips.py`

Expected: PASS.

- [ ] **Step 3: Commit all requested changes**

Run: `git status --short`, then `git add -A`, then commit with:

```bash
git commit -m "feat(ui): improve terminal readability"
```
