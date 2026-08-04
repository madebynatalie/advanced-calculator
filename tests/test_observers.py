"""Tests for calculator observers."""

from unittest.mock import Mock

import pytest

from app.observers import AutoSaveObserver, LoggingObserver


@pytest.fixture
def calculator_mock():
    """Create a calculator-like mock object."""
    calculator = Mock()
    calculator.history_count = 3
    calculator.config.auto_save = True
    calculator.save_history = Mock()

    return calculator


def test_logging_observer_prints_history_count(
    calculator_mock,
    capsys,
):
    """Test that the logging observer reports the history size."""
    observer = LoggingObserver()

    observer.update(calculator_mock)

    captured = capsys.readouterr()

    assert (
        "Calculation history now contains 3 calculations."
        in captured.out
    )


def test_auto_save_observer_saves_when_enabled(
    calculator_mock,
):
    """Test that auto-save runs when enabled."""
    observer = AutoSaveObserver()

    observer.update(calculator_mock)

    calculator_mock.save_history.assert_called_once()


def test_auto_save_observer_does_not_save_when_disabled(
    calculator_mock,
):
    """Test that auto-save does not run when disabled."""
    calculator_mock.config.auto_save = False
    observer = AutoSaveObserver()

    observer.update(calculator_mock)

    calculator_mock.save_history.assert_not_called()