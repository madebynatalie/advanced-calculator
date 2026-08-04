"""Command-line calculator facade and REPL interface."""

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorCaretaker
from app.history import History


class Calculator:
    """
    Provide a simplified interface to the calculator subsystems.

    This class represents the Facade design pattern because it coordinates
    configuration, history management, and undo/redo state management.
    """

    def __init__(
        self,
        config: CalculatorConfig | None = None,
    ) -> None:
        """Initialize the calculator and load existing history."""
        self.config = config or CalculatorConfig.from_env()
        self.history = History(self.config.history_file)
        self.caretaker = CalculatorCaretaker()

        self._load_history_on_startup()

    def _load_history_on_startup(self) -> None:
        """Automatically load history when its CSV file exists."""
        if self.history.file_path.exists():
            self.history.load()

    @property
    def history_count(self) -> int:
        """Return the number of calculations stored in history."""
        return len(self.history)

    def show_help(self) -> str:
        """Return a help message describing supported commands."""
        return (
            "\nAvailable Commands:\n"
            "  add <a> <b>\n"
            "  subtract <a> <b>\n"
            "  multiply <a> <b>\n"
            "  divide <a> <b>\n"
            "  power <a> <b>\n"
            "  root <a> <b>\n\n"
            "Other Commands:\n"
            "  history\n"
            "  clear\n"
            "  undo\n"
            "  redo\n"
            "  save\n"
            "  load\n"
            "  help\n"
            "  exit"
        )

    def show_history(self) -> str:
        """Return the formatted calculation history."""
        return str(self.history)

    def clear_history(self) -> None:
        """Clear all calculation history."""
        self.caretaker.save_state(self.history)
        self.history.clear()

    def save_history(self) -> None:
        """Save history to disk."""
        self.history.save()

    def load_history(self) -> None:
        """Load history from disk."""
        self.history.load()

    def execute_calculation(
        self,
        first_number,
        second_number,
        operation_name: str,
    ) -> Calculation:
        """Create, store, and optionally save a calculation."""
        self.caretaker.save_state(self.history)

        calculation = Calculation(
            first_number,
            second_number,
            operation_name,
        )

        self.history.add(calculation)
        self._trim_history()

        if self.config.auto_save:
            self.history.save()

        return calculation

    def undo(self) -> None:
        """Undo the most recent calculator state change."""
        self.caretaker.undo(self.history)

        if self.config.auto_save:
            self.history.save()

    def redo(self) -> None:
        """Redo the most recently undone calculator state change."""
        self.caretaker.redo(self.history)

        if self.config.auto_save:
            self.history.save()

    def _trim_history(self) -> None:
        """Keep history within the configured maximum size."""
        if len(self.history) <= self.config.max_history:
            return

        trimmed_dataframe = self.history.dataframe.tail(
            self.config.max_history
        )

        self.history.restore(trimmed_dataframe)