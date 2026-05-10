"""Tests for telemetry.errors.report_handled_error."""

from __future__ import annotations

from unittest.mock import patch

import pytest

import pythinker_code.telemetry as telemetry_mod
from pythinker_code.telemetry import set_context
from pythinker_code.telemetry.errors import report_handled_error


@pytest.fixture(autouse=True)
def _reset_telemetry_state():
    telemetry_mod._event_queue.clear()
    telemetry_mod._device_id = None
    telemetry_mod._session_id = None
    telemetry_mod._client_info = None
    telemetry_mod._session_started_sessions.clear()
    telemetry_mod._sink = None
    telemetry_mod._disabled = False
    yield
    telemetry_mod._event_queue.clear()
    telemetry_mod._device_id = None
    telemetry_mod._session_id = None
    telemetry_mod._client_info = None
    telemetry_mod._session_started_sessions.clear()
    telemetry_mod._sink = None
    telemetry_mod._disabled = False


def test_emits_track_event_with_site_and_exc_class():
    set_context(device_id="dev1", session_id="sess1")
    exc = ValueError("boom")
    with patch("pythinker_code.telemetry.errors._sentry.capture_exception"):
        report_handled_error(exc, site="tool.read", tool="ReadFile")

    assert len(telemetry_mod._event_queue) == 1
    record = telemetry_mod._event_queue[0]
    assert record["event"] == "error"
    assert record["properties"]["site"] == "tool.read"
    assert record["properties"]["exc_class"] == "ValueError"
    assert record["properties"]["tool"] == "ReadFile"


def test_forwards_to_sentry():
    set_context(device_id="dev1", session_id="sess1")
    exc = RuntimeError("explode")
    with patch("pythinker_code.telemetry.errors._sentry.capture_exception") as mock_capture:
        report_handled_error(exc, site="tool.write", tool="WriteFile")
    mock_capture.assert_called_once_with(exc)


def test_extra_attrs_pass_through():
    set_context(device_id="dev1", session_id="sess1")
    with patch("pythinker_code.telemetry.errors._sentry.capture_exception"):
        report_handled_error(
            OSError("nope"),
            site="tool.shell.exec",
            tool="Shell",
            background=False,
            timeout_s=30,
        )
    record = telemetry_mod._event_queue[0]
    assert record["properties"]["background"] is False
    assert record["properties"]["timeout_s"] == 30


def test_track_failure_does_not_raise():
    """If track() somehow raises, the helper must swallow and still call Sentry."""
    set_context(device_id="dev1", session_id="sess1")
    with (
        patch("pythinker_code.telemetry.errors.track", side_effect=RuntimeError("track broke")),
        patch("pythinker_code.telemetry.errors._sentry.capture_exception") as mock_capture,
    ):
        report_handled_error(ValueError("x"), site="tool.read", tool="ReadFile")
    # Sentry path still ran
    mock_capture.assert_called_once()


def test_sentry_failure_does_not_raise():
    """If Sentry raises, the helper must swallow."""
    set_context(device_id="dev1", session_id="sess1")
    with patch(
        "pythinker_code.telemetry.errors._sentry.capture_exception",
        side_effect=RuntimeError("sentry broke"),
    ):
        # No assertion: just verify no exception escapes.
        report_handled_error(ValueError("x"), site="tool.read", tool="ReadFile")
    # Track path still ran
    assert len(telemetry_mod._event_queue) == 1


def test_disabled_telemetry_skips_track_but_still_calls_sentry():
    """When telemetry is disabled, track is a no-op; Sentry capture is still invoked
    because the Sentry SDK has its own opt-out path (PYTHINKER_DISABLE_TELEMETRY
    short-circuits inside sentry.init, not at capture time)."""
    telemetry_mod._disabled = True
    with patch("pythinker_code.telemetry.errors._sentry.capture_exception") as mock_capture:
        report_handled_error(ValueError("x"), site="tool.read", tool="ReadFile")
    assert len(telemetry_mod._event_queue) == 0
    mock_capture.assert_called_once()


def test_no_tool_argument_is_optional():
    set_context(device_id="dev1", session_id="sess1")
    with patch("pythinker_code.telemetry.errors._sentry.capture_exception"):
        report_handled_error(KeyError("missing"), site="auth.oauth.refresh")
    record = telemetry_mod._event_queue[0]
    assert "tool" not in record["properties"]
    assert record["properties"]["site"] == "auth.oauth.refresh"
    assert record["properties"]["exc_class"] == "KeyError"
