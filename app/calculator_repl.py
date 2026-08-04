"""Command-line calculator facade and REPL interface."""

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