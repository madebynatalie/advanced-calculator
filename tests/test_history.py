"""Tests for pandas-based calculation history."""

from pathlib import Path

import pandas as pd
import pytest

from app.calculation import Calculation
from app.exceptions import HistoryError
from app.history import History


@pytest.fixture
def history(tmp_path):
    """Create a History object using a temporary CSV file."""
    return History(tmp_path / "history.csv")


@pytest.mark.parametrize(
    "first, second, operation, expected_result",
    [
        (5, 3, "add", 8),
        (10, 4, "subtract", 6),
        (3, 7, "multiply", 21),
        (20, 5, "divide", 4),
    ],
)
def test_add_calculation(
    history,
    first,
    second,
    operation,
    expected_result,
):
    """Test adding calculations to a DataFrame."""
    calculation = Calculation(first, second, operation)

    history.add(calculation)

    assert len(history) == 1
    assert history.dataframe.iloc[0]["Result"] == pytest.approx(
        expected_result
    )


def test_add_rejects_non_calculation(history):
    """Test that history rejects invalid object types."""
    with pytest.raises(
        HistoryError,
        match="History can only store Calculation objects.",
    ):
        history.add("not a calculation")


def test_dataframe_returns_copy(history):
    """Test that the public DataFrame cannot alter internal history."""
    history.add(Calculation(5, 3, "add"))

    copied_dataframe = history.dataframe
    copied_dataframe.loc[0, "Result"] = 100

    assert history.dataframe.loc[0, "Result"] == pytest.approx(8)


def test_clear_history(history):
    """Test clearing all calculation history."""
    history.add(Calculation(5, 3, "add"))
    history.add(Calculation(10, 2, "divide"))

    history.clear()

    assert len(history) == 0
    assert list(history.dataframe.columns) == History.COLUMNS


def test_save_history(history):
    """Test saving history to CSV."""
    history.add(Calculation(5, 3, "add"))

    history.save()

    assert history.file_path.exists()

    saved_dataframe = pd.read_csv(history.file_path)
    assert len(saved_dataframe) == 1
    assert saved_dataframe.iloc[0]["Result"] == pytest.approx(8)


def test_save_to_custom_path(history, tmp_path):
    """Test saving history to a supplied file path."""
    custom_path = tmp_path / "custom" / "saved.csv"
    history.add(Calculation(6, 2, "multiply"))

    history.save(custom_path)

    assert custom_path.exists()


def test_load_history(history):
    """Test loading valid calculation history from CSV."""
    original_history = History(history.file_path)
    original_history.add(Calculation(9, 3, "divide"))
    original_history.save()

    history.load()

    assert len(history) == 1
    assert history.dataframe.iloc[0]["Result"] == pytest.approx(3)


def test_load_from_custom_path(history, tmp_path):
    """Test loading history from a supplied file path."""
    custom_path = tmp_path / "custom.csv"

    pd.DataFrame(
        [
            {
                "First Number": 2.0,
                "Second Number": 4.0,
                "Operation": "power",
                "Result": 16.0,
            }
        ]
    ).to_csv(custom_path, index=False)

    history.load(custom_path)

    assert len(history) == 1
    assert history.dataframe.iloc[0]["Operation"] == "power"


def test_load_missing_file(history):
    """Test loading a nonexistent file."""
    with pytest.raises(
        HistoryError,
        match="History file does not exist:",
    ):
        history.load()


def test_load_missing_columns(history):
    """Test loading a CSV with an invalid structure."""
    pd.DataFrame(
        [{"Operation": "add", "Result": 8}]
    ).to_csv(history.file_path, index=False)

    with pytest.raises(
        HistoryError,
        match="History file is missing required columns.",
    ):
        history.load()


def test_get_last_empty_history(history):
    """Test getting the latest entry from empty history."""
    assert history.get_last() is None


def test_get_last_entry(history):
    """Test retrieving the latest calculation."""
    history.add(Calculation(5, 3, "add"))
    history.add(Calculation(10, 2, "divide"))

    last_entry = history.get_last()

    assert last_entry["Operation"] == "divide"
    assert last_entry["Result"] == pytest.approx(5)


def test_remove_last_empty_history(history):
    """Test removing an entry from empty history."""
    assert history.remove_last() is None


def test_remove_last_entry(history):
    """Test removing and returning the latest calculation."""
    history.add(Calculation(5, 3, "add"))
    history.add(Calculation(10, 2, "divide"))

    removed_entry = history.remove_last()

    assert removed_entry["Operation"] == "divide"
    assert len(history) == 1
    assert history.get_last()["Operation"] == "add"


def test_restore_dataframe(history):
    """Test restoring history from a valid DataFrame."""
    dataframe = pd.DataFrame(
        [
            {
                "First Number": 4.0,
                "Second Number": 5.0,
                "Operation": "multiply",
                "Result": 20.0,
            }
        ]
    )

    history.restore(dataframe)

    assert len(history) == 1
    assert history.get_last()["Result"] == pytest.approx(20)


@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        [],
        {},
        "invalid",
    ],
)
def test_restore_rejects_non_dataframe(history, invalid_value):
    """Test restoring history from invalid values."""
    with pytest.raises(
        HistoryError,
        match="History can only be restored from a DataFrame.",
    ):
        history.restore(invalid_value)


def test_restore_rejects_missing_columns(history):
    """Test restoring an improperly structured DataFrame."""
    dataframe = pd.DataFrame(
        [{"Operation": "add", "Result": 8}]
    )

    with pytest.raises(
        HistoryError,
        match="DataFrame is missing required history columns.",
    ):
        history.restore(dataframe)


def test_string_empty_history(history):
    """Test the string representation of empty history."""
    assert str(history) == "No calculations in history."


def test_string_populated_history(history):
    """Test the string representation of populated history."""
    history.add(Calculation(5, 3, "add"))

    output = str(history)

    assert "First Number" in output
    assert "Operation" in output
    assert "add" in output
    assert "8.0" in output