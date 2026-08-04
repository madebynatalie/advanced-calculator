"""Tests for calculator memento undo and redo support."""

import pandas as pd
import pytest

from app.calculation import Calculation
from app.calculator_memento import (
    CalculatorCaretaker,
    CalculatorMemento,
)
from app.exceptions import UndoRedoError
from app.history import History


@pytest.fixture
def history(tmp_path):
    """Create temporary calculator history."""
    return History(tmp_path / "history.csv")


@pytest.fixture
def caretaker():
    """Create an empty calculator caretaker."""
    return CalculatorCaretaker()


def test_memento_stores_dataframe_copy():
    """Test that a memento protects its original state."""
    dataframe = pd.DataFrame(
        [
            {
                "First Number": 5.0,
                "Second Number": 3.0,
                "Operation": "add",
                "Result": 8.0,
            }
        ]
    )

    memento = CalculatorMemento(dataframe)
    dataframe.loc[0, "Result"] = 100

    assert memento.get_state().loc[0, "Result"] == pytest.approx(8)


def test_get_state_returns_copy():
    """Test that retrieving state cannot modify the memento."""
    dataframe = pd.DataFrame(
        [
            {
                "First Number": 5.0,
                "Second Number": 3.0,
                "Operation": "add",
                "Result": 8.0,
            }
        ]
    )

    memento = CalculatorMemento(dataframe)
    retrieved_state = memento.get_state()
    retrieved_state.loc[0, "Result"] = 200

    assert memento.get_state().loc[0, "Result"] == pytest.approx(8)


@pytest.mark.parametrize(
    "invalid_state",
    [
        None,
        [],
        {},
        "invalid",
    ],
)
def test_memento_rejects_non_dataframe(invalid_state):
    """Test that mementos require pandas DataFrames."""
    with pytest.raises(
        UndoRedoError,
        match="A calculator memento requires a pandas DataFrame.",
    ):
        CalculatorMemento(invalid_state)


def test_save_state_enables_undo(history, caretaker):
    """Test saving a state makes undo available."""
    assert caretaker.can_undo is False

    caretaker.save_state(history)

    assert caretaker.can_undo is True
    assert caretaker.can_redo is False


def test_undo_restores_previous_state(history, caretaker):
    """Test undo restores history before its latest change."""
    history.add(Calculation(5, 3, "add"))

    caretaker.save_state(history)
    history.add(Calculation(10, 2, "divide"))

    caretaker.undo(history)

    assert len(history) == 1
    assert history.get_last()["Operation"] == "add"
    assert caretaker.can_redo is True


def test_redo_restores_undone_state(history, caretaker):
    """Test redo restores the state removed by undo."""
    history.add(Calculation(5, 3, "add"))

    caretaker.save_state(history)
    history.add(Calculation(10, 2, "divide"))

    caretaker.undo(history)
    caretaker.redo(history)

    assert len(history) == 2
    assert history.get_last()["Operation"] == "divide"
    assert caretaker.can_undo is True


def test_new_saved_state_clears_redo_stack(history, caretaker):
    """Test making a new change after undo removes redo history."""
    caretaker.save_state(history)
    history.add(Calculation(5, 3, "add"))

    caretaker.undo(history)

    assert caretaker.can_redo is True

    caretaker.save_state(history)

    assert caretaker.can_redo is False


def test_multiple_undo_operations(history, caretaker):
    """Test undoing multiple history changes."""
    caretaker.save_state(history)
    history.add(Calculation(5, 3, "add"))

    caretaker.save_state(history)
    history.add(Calculation(10, 2, "divide"))

    caretaker.undo(history)
    assert len(history) == 1

    caretaker.undo(history)
    assert len(history) == 0


def test_multiple_redo_operations(history, caretaker):
    """Test redoing multiple undone history changes."""
    caretaker.save_state(history)
    history.add(Calculation(5, 3, "add"))

    caretaker.save_state(history)
    history.add(Calculation(10, 2, "divide"))

    caretaker.undo(history)
    caretaker.undo(history)

    caretaker.redo(history)
    assert len(history) == 1

    caretaker.redo(history)
    assert len(history) == 2


def test_undo_without_saved_state_raises_error(history, caretaker):
    """Test undo fails when no previous state exists."""
    with pytest.raises(
        UndoRedoError,
        match="Nothing to undo.",
    ):
        caretaker.undo(history)


def test_redo_without_saved_state_raises_error(history, caretaker):
    """Test redo fails when no redo state exists."""
    with pytest.raises(
        UndoRedoError,
        match="Nothing to redo.",
    ):
        caretaker.redo(history)


@pytest.mark.parametrize(
    "invalid_history",
    [
        None,
        [],
        {},
        "invalid",
    ],
)
def test_save_state_rejects_invalid_history(
    caretaker,
    invalid_history,
):
    """Test saving requires a History object."""
    with pytest.raises(
        UndoRedoError,
        match="The caretaker can only save a History object.",
    ):
        caretaker.save_state(invalid_history)


@pytest.mark.parametrize(
    "invalid_history",
    [
        None,
        [],
        {},
        "invalid",
    ],
)
def test_undo_rejects_invalid_history(
    caretaker,
    invalid_history,
):
    """Test undo requires a History object."""
    with pytest.raises(
        UndoRedoError,
        match="Undo requires a History object.",
    ):
        caretaker.undo(invalid_history)


@pytest.mark.parametrize(
    "invalid_history",
    [
        None,
        [],
        {},
        "invalid",
    ],
)
def test_redo_rejects_invalid_history(
    caretaker,
    invalid_history,
):
    """Test redo requires a History object."""
    with pytest.raises(
        UndoRedoError,
        match="Redo requires a History object.",
    ):
        caretaker.redo(invalid_history)


def test_clear_removes_all_saved_states(history, caretaker):
    """Test clearing the caretaker resets undo and redo."""
    caretaker.save_state(history)
    history.add(Calculation(5, 3, "add"))
    caretaker.undo(history)

    caretaker.clear()

    assert caretaker.can_undo is False
    assert caretaker.can_redo is False