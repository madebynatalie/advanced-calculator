"""Tests for the calculator facade and REPL interface."""

import app.calculator_repl as repl_module
import pandas as pd
import pytest

from app.exceptions import CalculatorError
from app.calculation import Calculation 
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorCaretaker
from app.calculator_repl import Calculator
from app.history import History
from unittest.mock import Mock 


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
@pytest.mark.parametrize(
        "command, expected_message",
    [
            ("", "Please enter a command."),
            ("   ", "Please enter a command."),
            ("add", "Use the format:"),
            ("add 5", "Use the format:"),
            ("add 5 3 extra", "Use the format:"),
            ("help extra", "does not accept arguments"),
            ("history extra", "does not accept arguments"),
    ],
)
def test_process_command_rejects_invalid_format(
    calculator_config,
    command,
    expected_message,
):
    calculator = Calculator(calculator_config)

    message, should_continue = calculator.process_command(command)

    assert expected_message in message
    assert should_continue is True


@pytest.mark.parametrize(
    "command, expected_result",
    [
        ("add 5 3", 8),
        ("subtract 10 4", 6),
        ("multiply 3 7", 21),
        ("divide 20 5", 4),
        ("power 2 3", 8),
        ("root 9 2", 3),
    ],
)
def test_process_calculation_command(
    calculator_config,
    command,
    expected_result,
):
    calculator = Calculator(calculator_config)

    message, should_continue = calculator.process_command(command)

    assert message == f"Result: {float(expected_result)}"
    assert should_continue is True
    assert calculator.history_count == 1


def test_process_help_command(calculator_config):
    calculator = Calculator(calculator_config)

    message, should_continue = calculator.process_command("help")

    assert "Available Commands" in message
    assert should_continue is True


def test_process_history_command(calculator_config):
    calculator = Calculator(calculator_config)
    calculator.execute_calculation(5, 3, "add")

    message, should_continue = calculator.process_command("history")

    assert "add" in message
    assert "8.0" in message
    assert should_continue is True


def test_process_clear_command(calculator_config):
    calculator = Calculator(calculator_config)
    calculator.execute_calculation(5, 3, "add")

    message, should_continue = calculator.process_command("clear")

    assert message == "History cleared."
    assert calculator.history_count == 0
    assert should_continue is True


def test_process_undo_and_redo_commands(calculator_config):
    calculator = Calculator(calculator_config)
    calculator.execute_calculation(5, 3, "add")

    undo_message, undo_continue = calculator.process_command("undo")

    assert undo_message == "Last action undone."
    assert undo_continue is True
    assert calculator.history_count == 0

    redo_message, redo_continue = calculator.process_command("redo")

    assert redo_message == "Last action restored."
    assert redo_continue is True
    assert calculator.history_count == 1


def test_process_save_command(calculator_config):
    calculator = Calculator(calculator_config)
    calculator.execute_calculation(5, 3, "add")

    message, should_continue = calculator.process_command("save")

    assert message == "History saved."
    assert calculator.history.file_path.exists()
    assert should_continue is True


def test_process_load_command(calculator_config):
    calculator = Calculator(calculator_config)
    calculator.execute_calculation(5, 3, "add")
    calculator.save_history()
    calculator.clear_history()

    message, should_continue = calculator.process_command("load")

    assert message == "History loaded."
    assert calculator.history_count == 1
    assert calculator.caretaker.can_undo is False
    assert should_continue is True


@pytest.mark.parametrize("command", ["exit", "quit", " EXIT "])
def test_process_exit_command(calculator_config, command):
    calculator = Calculator(calculator_config)

    message, should_continue = calculator.process_command(command)

    assert message == "Goodbye!"
    assert should_continue is False

def test_run_exits_normally(
    calculator_config,
    monkeypatch,
    capsys,
):
    """Test the normal interactive REPL exit path."""
    calculator = Calculator(calculator_config)

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "exit",
    )

    calculator.run()

    output = capsys.readouterr().out

    assert "Advanced Calculator" in output
    assert "Goodbye!" in output


def test_run_handles_calculator_error(
    calculator_config,
    monkeypatch,
    capsys,
):
    """Test that calculator errors do not terminate the REPL."""
    calculator = Calculator(calculator_config)

    user_inputs = iter(["bad command", "exit"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )

    original_process_command = calculator.process_command
    call_count = 0

    def process_with_error(user_input):
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            raise CalculatorError("Test calculator error")

        return original_process_command(user_input)

    monkeypatch.setattr(
        calculator,
        "process_command",
        process_with_error,
    )

    calculator.run()

    output = capsys.readouterr().out

    assert "Error: Test calculator error" in output
    assert "Goodbye!" in output


@pytest.mark.parametrize(
    "input_error",
    [
        EOFError(),
        KeyboardInterrupt(),
    ],
)
def test_run_handles_terminal_exit(
    calculator_config,
    monkeypatch,
    capsys,
    input_error,
):
    """Test EOF and keyboard-interrupt exit behavior."""
    calculator = Calculator(calculator_config)

    def raise_input_error(prompt):
        raise input_error

    monkeypatch.setattr(
        "builtins.input",
        raise_input_error,
    )

    calculator.run()

    output = capsys.readouterr().out

    assert "Goodbye!" in output

def test_main_starts_calculator(monkeypatch):
    """Test that main creates and runs the calculator."""
    fake_calculator = Mock()

    monkeypatch.setattr(
        repl_module,
        "Calculator",
        lambda: fake_calculator,
    )

    repl_module.main()

    fake_calculator.run.assert_called_once()


def test_main_handles_startup_error(
    monkeypatch,
    capsys,
):
    """Test startup configuration or history errors."""

    def raise_startup_error():
        raise CalculatorError("Startup failed")

    monkeypatch.setattr(
        repl_module,
        "Calculator",
        raise_startup_error,
    )

    repl_module.main()

    output = capsys.readouterr().out

    assert (
        "Unable to start calculator: Startup failed"
        in output
    )
def test_run_continues_after_normal_command(
    calculator_config,
    monkeypatch,
    capsys,
):
    """Test that the REPL continues after processing a command."""
    calculator = Calculator(calculator_config)

    user_inputs = iter(
        [
            "add 5 3",
            "exit",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )

    calculator.run()

    output = capsys.readouterr().out

    assert "Result: 8.0" in output
    assert "Goodbye!" in output