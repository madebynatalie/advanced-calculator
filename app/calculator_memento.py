"""Memento pattern support for calculator undo and redo."""

from dataclasses import dataclass, field

import pandas as pd

from app.exceptions import UndoRedoError
from app.history import History


@dataclass(frozen=True)
class CalculatorMemento:
    """Store an immutable snapshot of calculator history."""

    history_state: pd.DataFrame = field(repr=False)

    def __post_init__(self):
        """Protect the saved state from outside modification."""
        if not isinstance(self.history_state, pd.DataFrame):
            raise UndoRedoError(
                "A calculator memento requires a pandas DataFrame."
            )

        object.__setattr__(
            self,
            "history_state",
            self.history_state.copy(deep=True),
        )

    def get_state(self) -> pd.DataFrame:
        """Return a copy of the saved history state."""
        return self.history_state.copy(deep=True)


class CalculatorCaretaker:
    """Manage calculator history snapshots for undo and redo."""

    def __init__(self):
        """Initialize empty undo and redo stacks."""
        self._undo_stack: list[CalculatorMemento] = []
        self._redo_stack: list[CalculatorMemento] = []

    def save_state(self, history: History) -> None:
        """Save the current history state before a change occurs."""
        if not isinstance(history, History):
            raise UndoRedoError(
                "The caretaker can only save a History object."
            )

        self._undo_stack.append(
            CalculatorMemento(history.dataframe)
        )

        self._redo_stack.clear()

    def undo(self, history: History) -> None:
        """Restore the most recently saved history state."""
        if not isinstance(history, History):
            raise UndoRedoError(
                "Undo requires a History object."
            )

        if not self._undo_stack:
            raise UndoRedoError("Nothing to undo.")

        self._redo_stack.append(
            CalculatorMemento(history.dataframe)
        )

        previous_state = self._undo_stack.pop()
        history.restore(previous_state.get_state())

    def redo(self, history: History) -> None:
        """Restore the most recently undone history state."""
        if not isinstance(history, History):
            raise UndoRedoError(
                "Redo requires a History object."
            )

        if not self._redo_stack:
            raise UndoRedoError("Nothing to redo.")

        self._undo_stack.append(
            CalculatorMemento(history.dataframe)
        )

        next_state = self._redo_stack.pop()
        history.restore(next_state.get_state())

    @property
    def can_undo(self) -> bool:
        """Return whether an undo state is available."""
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        """Return whether a redo state is available."""
        return bool(self._redo_stack)

    def clear(self) -> None:
        """Clear all saved undo and redo states."""
        self._undo_stack.clear()
        self._redo_stack.clear()