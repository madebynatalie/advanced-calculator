"""Command-line calculator facade and REPL interface."""

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorCaretaker
from app.exceptions import CalculatorError
from app.history import History
from app.input_validators import validate_operation_name
from app.observers import AutoSaveObserver, LoggingObserver


class Calculator:
    """
    Provide a simplified interface to the calculator subsystems.

    This class represents the Facade design pattern because it coordinates
    configuration, history, calculation execution, undo/redo, observers,
    and command processing.
    """

    def __init__(
        self,
        config: CalculatorConfig | None = None,
    ) -> None:
        """Initialize the calculator and load existing history."""
        self.config = config or CalculatorConfig.from_env()
        self.history = History(self.config.history_file)
        self.caretaker = CalculatorCaretaker()

        self.observers = [
            LoggingObserver(),
            AutoSaveObserver(),
        ]

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
        """Create, store, and notify observers of a calculation."""
        self.caretaker.save_state(self.history)

        calculation = Calculation(
            first_number,
            second_number,
            operation_name,
        )

        self.history.add(calculation)
        self._trim_history()
        self.notify_observers()

        return calculation

    def undo(self) -> None:
        """Undo the most recent calculator state change."""
        self.caretaker.undo(self.history)
        self.notify_observers()

    def redo(self) -> None:
        """Redo the most recently undone calculator state change."""
        self.caretaker.redo(self.history)
        self.notify_observers()

    def _trim_history(self) -> None:
        """Keep history within the configured maximum size."""
        if len(self.history) <= self.config.max_history:
            return

        trimmed_dataframe = self.history.dataframe.tail(
            self.config.max_history
        )

        self.history.restore(trimmed_dataframe)

    def process_command(self, user_input: str) -> tuple[str, bool]:
        """
        Process one user command.

        Return a message and whether the REPL should continue.
        """
        stripped_input = user_input.strip()

        if not stripped_input:
            return "Please enter a command.", True

        parts = stripped_input.split()
        command = parts[0].lower()

        command_handlers = {
            "help": self._handle_help,
            "history": self._handle_history,
            "clear": self._handle_clear,
            "undo": self._handle_undo,
            "redo": self._handle_redo,
            "save": self._handle_save,
            "load": self._handle_load,
            "exit": self._handle_exit,
            "quit": self._handle_exit,
        }

        handler = command_handlers.get(command)

        if handler is not None:
            if len(parts) != 1:
                return (
                    f"The '{command}' command does not accept arguments.",
                    True,
                )

            return handler()

        return self._handle_calculation(parts)

    def _handle_calculation(
        self,
        parts: list[str],
    ) -> tuple[str, bool]:
        """Process an arithmetic operation command."""
        if len(parts) != 3:
            return (
                "Use the format: <operation> <first number> "
                "<second number>.",
                True,
            )

        operation_name, first_number, second_number = parts
        operation_name = validate_operation_name(operation_name)

        calculation = self.execute_calculation(
            first_number,
            second_number,
            operation_name,
        )

        return f"Result: {calculation.result}", True

    def _handle_help(self) -> tuple[str, bool]:
        """Process the help command."""
        return self.show_help(), True

    def _handle_history(self) -> tuple[str, bool]:
        """Process the history command."""
        return self.show_history(), True

    def _handle_clear(self) -> tuple[str, bool]:
        """Process the clear command."""
        self.clear_history()
        self.notify_observers()

        return "History cleared.", True

    def _handle_undo(self) -> tuple[str, bool]:
        """Process the undo command."""
        self.undo()
        return "Last action undone.", True

    def _handle_redo(self) -> tuple[str, bool]:
        """Process the redo command."""
        self.redo()
        return "Last action restored.", True

    def _handle_save(self) -> tuple[str, bool]:
        """Process the save command."""
        self.save_history()
        return "History saved.", True

    def _handle_load(self) -> tuple[str, bool]:
        """Process the load command."""
        self.load_history()
        self.caretaker.clear()

        return "History loaded.", True

    @staticmethod
    def _handle_exit() -> tuple[str, bool]:
        """Process the exit command."""
        return "Goodbye!", False

    def notify_observers(self) -> None:
        """Notify all registered observers."""
        for observer in self.observers:
            observer.update(self)

    def run(self) -> None:
        """Run the calculator Read-Eval-Print Loop."""
        print("Advanced Calculator")
        print("Enter 'help' to view available commands.")

        while True:
            try:
                user_input = input("calculator> ")

                message, should_continue = self.process_command(
                    user_input
                )

                print(message)

                if not should_continue:
                    break

            except CalculatorError as error:
                print(f"Error: {error}")

            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break


def main() -> None:
    """Start the calculator application."""
    try:
        calculator = Calculator()
        calculator.run()
    except CalculatorError as error:
        print(f"Unable to start calculator: {error}")


if __name__ == "__main__":  # pragma: no cover
    main()