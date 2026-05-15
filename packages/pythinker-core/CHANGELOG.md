# Pythinker Core Changelog

## 1.1.0 (2026-05-13)

Strict-interleaved reasoning replay for Kimi K2.x and DeepSeek, plus the SDK 0.101 anthropic compat fix.

- **`contrib.chat_provider.openai_legacy._convert_message`** — for strict-interleaved providers (`kimi-k2*`, `deepseek*`) now **always** emits `reasoning_content` on assistant turns, even when no `ThinkPart` was captured. Falls back to the assistant text, then to `"[reasoning unavailable]"` so Kimi-style "thinking is enabled but reasoning_content is missing in assistant tool call message at index N" rejections no longer trip multi-step tool flows. Fixes pythinker-code [#37](https://github.com/mohamed-elkholy95/Pythinker-Code/issues/37).
- **`chat_provider.pythinker`** — same `reasoning_content` replay guarantee on the native pythinker provider for parity.
- **`contrib.chat_provider.anthropic`** — added `case _:` fallbacks at the prompt-cache-injection site and the streaming content-block start site so the six new tool-result block types in anthropic SDK 0.101 (`web_fetch_tool_result`, `code_execution_tool_result`, `bash_code_execution_tool_result`, `text_editor_code_execution_tool_result`, `tool_search_tool_result`, `container_upload`) don't trip `pyright`'s exhaustive-match check.
- No public API changes; minor patch contract — drop-in upgrade.

## 1.0.0 (2026-05-06)

- Initial public release of Pythinker Core: LLM, message, provider, and tool abstractions.
