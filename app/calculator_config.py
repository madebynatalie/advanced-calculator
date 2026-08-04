"""Configuration management for the calculator application."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from app.exceptions import ConfigurationError


@dataclass(frozen=True)
class CalculatorConfig:
    """Store validated calculator configuration settings."""

    history_file: str
    auto_save: bool
    max_history: int
    log_level: str

    @classmethod
    def from_env(cls) -> "CalculatorConfig":
        """Create configuration from environment variables."""

        load_dotenv()

        history_file = os.getenv(
            "CALCULATOR_HISTORY_FILE",
            "data/calculation_history.csv",
        )

        auto_save_text = os.getenv(
            "CALCULATOR_AUTO_SAVE",
            "true",
        )

        max_history_text = os.getenv(
            "CALCULATOR_MAX_HISTORY",
            "100",
        )

        log_level = os.getenv(
            "CALCULATOR_LOG_LEVEL",
            "INFO",
        ).strip().upper()

        auto_save = cls._parse_boolean(auto_save_text)
        max_history = cls._parse_max_history(max_history_text)
        log_level = cls._validate_log_level(log_level)

        if not history_file.strip():
            raise ConfigurationError(
                "CALCULATOR_HISTORY_FILE cannot be empty."
            )

        return cls(
            history_file=history_file.strip(),
            auto_save=auto_save,
            max_history=max_history,
            log_level=log_level,
        )

    @staticmethod
    def _parse_boolean(value: str) -> bool:
        """Convert a text environment value into a boolean."""

        normalized_value = value.strip().lower()

        if normalized_value in {"true", "1", "yes", "on"}:
            return True

        if normalized_value in {"false", "0", "no", "off"}:
            return False

        raise ConfigurationError(
            "CALCULATOR_AUTO_SAVE must be true or false."
        )

    @staticmethod
    def _parse_max_history(value: str) -> int:
        """Convert and validate the maximum history size."""

        try:
            max_history = int(value)
        except (TypeError, ValueError) as error:
            raise ConfigurationError(
                "CALCULATOR_MAX_HISTORY must be an integer."
            ) from error

        if max_history <= 0:
            raise ConfigurationError(
                "CALCULATOR_MAX_HISTORY must be greater than zero."
            )

        return max_history

    @staticmethod
    def _validate_log_level(value: str) -> str:
        """Validate the configured logging level."""

        valid_levels = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        if value not in valid_levels:
            raise ConfigurationError(
                "CALCULATOR_LOG_LEVEL is invalid."
            )

        return value