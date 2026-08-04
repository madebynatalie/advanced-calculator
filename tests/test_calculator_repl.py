"""Tests for the calculator facade and REPL interface."""

import pandas as pd
import pytest

from app.calculation import Calculation 
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
def test_execute_calculation_adds_to_history(calculator_config):
    calculator = Calculator(calculator_config)

    calculation = calculator.execute_calculation(5, 3, "add")

    assert isinstance(calculation, Calculation)
    assert calculation.result == pytest.approx(8)
    assert calculator.history_count == 1
    assert calculator.history.get_last()["Operation"] == "add"


def test_execute_calculation_auto_saves(calculator_config):
    calculator = Calculator(calculator_config)

    calculator.execute_calculation(10, 2, "divide")

    assert calculator.history.file_path.exists()


def test_execute_calculation_does_not_auto_save_when_disabled(
    tmp_path,
):
    config = CalculatorConfig(
        history_file=str(tmp_path / "history.csv"),
        auto_save=False,
        max_history=100,
        log_level="INFO",
    )

    calculator = Calculator(config)
    calculator.execute_calculation(5, 3, "add")

    assert calculator.history.file_path.exists() is False


def test_undo_removes_latest_calculation(calculator_config):
    calculator = Calculator(calculator_config)

    calculator.execute_calculation(5, 3, "add")
    calculator.execute_calculation(10, 2, "divide")

    calculator.undo()

    assert calculator.history_count == 1
    assert calculator.history.get_last()["Operation"] == "add"


def test_redo_restores_latest_calculation(calculator_config):
    calculator = Calculator(calculator_config)

    calculator.execute_calculation(5, 3, "add")
    calculator.execute_calculation(10, 2, "divide")

    calculator.undo()
    calculator.redo()

    assert calculator.history_count == 2
    assert calculator.history.get_last()["Operation"] == "divide"


def test_history_is_trimmed_to_configured_maximum(tmp_path):
    config = CalculatorConfig(
        history_file=str(tmp_path / "history.csv"),
        auto_save=False,
        max_history=2,
        log_level="INFO",
    )

    calculator = Calculator(config)

    calculator.execute_calculation(1, 1, "add")
    calculator.execute_calculation(2, 2, "add")
    calculator.execute_calculation(3, 3, "add")

    assert calculator.history_count == 2
    assert calculator.history.dataframe.iloc[0][
        "First Number"
    ] == pytest.approx(2)
    assert calculator.history.get_last()[
        "First Number"
    ] == pytest.approx(3)


def test_trim_history_does_nothing_when_within_limit(
    calculator_config,
):
    calculator = Calculator(calculator_config)

    calculator.execute_calculation(5, 3, "add")

    assert calculator.history_count == 1