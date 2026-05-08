# Readable Terminal Reports Design

## Goal

Improve shell output readability for long audit, search, and report responses, and make completed subagent worklog entries scannable.

## Current Problems

- Wide markdown tables with long cells are rendered as terminal columns, which causes words and paths to wrap into narrow vertical fragments.
- Completed subagent entries keep listing many child tool calls, so the completed state looks like an active trace instead of a summary.
- The user needs readable sections for reports and compact completed subagent summaries.

## Approved Direction

Use readable sections/cards for dense reports and collapse completed subagent blocks into summaries.

## Markdown Report Rendering

When a markdown table is too wide for terminal reading, render each row as a compact record instead of a multi-column table.

Adaptive table rendering should apply when a table has four or more columns or when its cell content is long enough that normal column layout would be hard to scan.

Each record should show the row number and then labeled fields, for example:

```text
1. Accessibility
   Issue: Search input relies on placeholder text only.
   Why it matters: Placeholder labels disappear during typing and are weak for screen readers.
   Suggested improvement: Add aria-label="Search sessions" or a visually hidden label.
   Priority: High
   Effort: XS
```

Small tables should keep the current table renderer.

## Completed Subagent Rendering

Running subagents should keep the current activity indicators.

Completed subagents should switch to a compact completion summary:

```text
✓ Subagent Audit web frontend completed
  explore · a143aa989 · 53 tool calls · 49 hidden
  ReadFile: 4 shown · web/src/..., vis/src/...
```

Errors should remain visible and should not be hidden behind the compact summary.

## Testing

- Add a markdown rendering regression test for wide report tables that verifies labeled records are rendered instead of narrow table columns.
- Add a worklog rendering regression test that verifies completed subagents show a summary and do not dump the full child tool-call list.
- Keep existing compact prompt, slash menu, worklog, and UI tests passing.

## Out Of Scope

- Changing model prompts or forcing the assistant to avoid markdown tables.
- Adding interactive expand/collapse controls for historical output.
- Reworking Rich Live architecture beyond the adaptive renderers needed here.
