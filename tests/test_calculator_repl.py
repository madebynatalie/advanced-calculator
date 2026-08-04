"""Tests for the calculator facade and REPL interface."""

import pandas as pd
import pytest

from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorCaretaker
from app.calculator_repl import Calculator
from app.history import History


@pytest.fixture
def calculator_config(tmp_path):
    """Create calculator configuration using a temporary history file."""

    return CalculatorConfig(
        history_file=str(tmp_path / "history.csv"),
        auto_save=True,
        max_history=100,
        log_level="INFO",
    )


def test_calculator_initializes_subsystems(calculator_config):
    """Test that the facade initializes its required components."""

    calculator = Calculator(calculator_config)

    assert calculator.config == calculator_config
    assert isinstance(calculator.history, History)
    assert isinstance(calculator.caretaker, CalculatorCaretaker)
    assert calculator.history_count == 0


def test_calculator_uses_environment_config_when_not_provided(
    monkeypatch,
    tmp_path,
):
    """Test configuration loading when no config object is provided."""

    history_path = tmp_path / "environment-history.csv"

    monkeypatch.setenv(
        "CALCULATOR_HISTORY_FILE",
        str(history_path),
    )
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY", "50")
    monkeypatch.setenv("CALCULATOR_LOG_LEVEL", "warning")

    calculator = Calculator()

    assert calculator.config.history_file == str(history_path)
    assert calculator.config.auto_save is False
    assert calculator.config.max_history == 50
    assert calculator.config.log_level == "WARNING"


def test_calculator_starts_empty_when_history_file_is_missing(
    calculator_config,
):
    """Test startup when no saved history file exists."""

    calculator = Calculator(calculator_config)

    assert calculator.history_count == 0
    assert calculator.history.dataframe.empty


def test_calculator_loads_existing_history(calculator_config):
    """Test automatic history loading during startup."""

    history_dataframe = pd.DataFrame(
        [
            {
                "First Number": 5.0,
                "Second Number": 3.0,
                "Operation": "add",
                "Result": 8.0,
            },
            {
                "First Number": 10.0,
                "Second Number": 2.0,
                "Operation": "divide",
                "Result": 5.0,
            },
        ]
    )

    history_dataframe.to_csv(
        calculator_config.history_file,
        index=False,
    )

    calculator = Calculator(calculator_config)

    assert calculator.history_count == 2
    assert calculator.history.get_last()["Operation"] == "divide"
    assert calculator.history.get_last()["Result"] == pytest.approx(5)