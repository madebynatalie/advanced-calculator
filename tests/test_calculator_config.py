"""Tests for calculator environment configuration."""

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


def clear_calculator_environment(monkeypatch):
    """Remove calculator environment variables before a test."""
    variable_names = [
        "CALCULATOR_HISTORY_FILE",
        "CALCULATOR_AUTO_SAVE",
        "CALCULATOR_MAX_HISTORY",
        "CALCULATOR_LOG_LEVEL",
    ]

    for variable_name in variable_names:
        monkeypatch.delenv(variable_name, raising=False)


def test_config_uses_default_values(monkeypatch):
    """Test default configuration values."""
    clear_calculator_environment(monkeypatch)

    config = CalculatorConfig.from_env()

    assert config.history_file == "data/calculation_history.csv"
    assert config.auto_save is True
    assert config.max_history == 100
    assert config.log_level == "INFO"


def test_config_reads_environment_values(monkeypatch):
    """Test configuration values supplied through the environment."""
    monkeypatch.setenv(
        "CALCULATOR_HISTORY_FILE",
        "custom/history.csv",
    )
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY", "250")
    monkeypatch.setenv("CALCULATOR_LOG_LEVEL", "debug")

    config = CalculatorConfig.from_env()

    assert config.history_file == "custom/history.csv"
    assert config.auto_save is False
    assert config.max_history == 250
    assert config.log_level == "DEBUG"


@pytest.mark.parametrize(
    "value, expected_result",
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("off", False),
    ],
)
def test_parse_boolean_valid_values(value, expected_result):
    """Test valid text representations of boolean values."""
    assert CalculatorConfig._parse_boolean(value) is expected_result


@pytest.mark.parametrize(
    "value",
    [
        "maybe",
        "enabled",
        "",
        "2",
    ],
)
def test_parse_boolean_rejects_invalid_values(value):
    """Test invalid boolean configuration values."""
    with pytest.raises(
        ConfigurationError,
        match="CALCULATOR_AUTO_SAVE must be true or false.",
    ):
        CalculatorConfig._parse_boolean(value)


@pytest.mark.parametrize(
    "value, expected_result",
    [
        ("1", 1),
        ("100", 100),
        ("250", 250),
    ],
)
def test_parse_max_history_valid_values(value, expected_result):
    """Test valid maximum-history values."""
    assert (
        CalculatorConfig._parse_max_history(value)
        == expected_result
    )


@pytest.mark.parametrize(
    "value",
    [
        "abc",
        "10.5",
        None,
    ],
)
def test_parse_max_history_rejects_non_integer(value):
    """Test maximum-history values that are not integers."""
    with pytest.raises(
        ConfigurationError,
        match="CALCULATOR_MAX_HISTORY must be an integer.",
    ):
        CalculatorConfig._parse_max_history(value)


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "-1",
        "-100",
    ],
)
def test_parse_max_history_rejects_non_positive_values(value):
    """Test maximum-history values below one."""
    with pytest.raises(
        ConfigurationError,
        match=(
            "CALCULATOR_MAX_HISTORY must be greater than zero."
        ),
    ):
        CalculatorConfig._parse_max_history(value)


@pytest.mark.parametrize(
    "value",
    [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ],
)
def test_validate_log_level_accepts_valid_values(value):
    """Test supported logging levels."""
    assert CalculatorConfig._validate_log_level(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "TRACE",
        "NOTICE",
        "",
        "INVALID",
    ],
)
def test_validate_log_level_rejects_invalid_values(value):
    """Test unsupported logging levels."""
    with pytest.raises(
        ConfigurationError,
        match="CALCULATOR_LOG_LEVEL is invalid.",
    ):
        CalculatorConfig._validate_log_level(value)


def test_empty_history_file_raises_error(monkeypatch):
    """Test that the history file path cannot be blank."""
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "   ")
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "true")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY", "100")
    monkeypatch.setenv("CALCULATOR_LOG_LEVEL", "INFO")

    with pytest.raises(
        ConfigurationError,
        match="CALCULATOR_HISTORY_FILE cannot be empty.",
    ):
        CalculatorConfig.from_env()


def test_invalid_auto_save_from_environment(monkeypatch):
    """Test invalid auto-save environment configuration."""
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "sometimes")

    with pytest.raises(ConfigurationError):
        CalculatorConfig.from_env()


def test_invalid_max_history_from_environment(monkeypatch):
    """Test invalid maximum-history environment configuration."""
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY", "many")

    with pytest.raises(ConfigurationError):
        CalculatorConfig.from_env()


def test_invalid_log_level_from_environment(monkeypatch):
    """Test invalid logging-level environment configuration."""
    monkeypatch.setenv("CALCULATOR_LOG_LEVEL", "LOUD")

    with pytest.raises(ConfigurationError):
        CalculatorConfig.from_env()

