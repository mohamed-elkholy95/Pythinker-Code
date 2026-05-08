# Codex Terminal UI Follow-Up Design

## Summary

Align the shell prompt, slash command menu, subagent activity rows, and diff summaries more closely with the Codex TUI reference in `.worktrees/codex-main` while preserving the existing prompt-toolkit and Rich architecture.

## Goals

- Keep the input surface compact by default, but allow it to grow with text up to five visible rows.
- Scroll input after five visible rows instead of clipping text to two rows.
- Keep slash commands in the Codex order: input area first, command list below it, status footer hidden while the list is active.
- Keep animated dots/particles for running subagent rows.
- Make diff cards compact and summary-first, with clear per-file added/removed counts.

## Non-Goals

- Replace prompt-toolkit with a custom TUI engine.
- Port Codex Rust state machines directly.
- Redesign unrelated welcome, history, auth, or modal flows.

## Design

The prompt buffer window should use a small preferred height with a maximum of five rows. The compact input background stays on the buffer window, and the prompt marker remains visually aligned with the first editable row.

The slash menu should remain an HSplit sibling directly below the prompt buffer, not a cursor-anchored float. This mirrors Codex's composer plus popup stack and avoids the clipped-popup bug caused by cursor floats inside a small input window.

Subagent rows should use a Rich dots spinner as the running indicator. Finished subagent child calls stay compact and dimmed, with errors still visually distinct.

Diff display should continue to group consecutive same-file diff blocks, but the rendered card should emphasize the file path and added/removed counts before showing hunk details.

## Testing

- Unit tests assert the prompt buffer grows to a max of five rows.
- Unit tests assert slash menu placement remains directly after the compact input layout node.
- Worklog tests assert running subagents render a dots spinner.
- Diff tests assert compact per-file summaries include added/removed counts.
- Run `tests/ui_and_conv` and targeted tmux slash completion tests.
