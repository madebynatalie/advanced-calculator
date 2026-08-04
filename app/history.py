"""Calculation history management using pandas."""

from pathlib import Path

import pandas as pd

from app.calculation import Calculation
from app.exceptions import HistoryError


class History:
    """Store, manage, save, and load calculator history."""

    COLUMNS = [
        "First Number",
        "Second Number",
        "Operation",
        "Result",
    ]

    def __init__(self, file_path: str = "data/calculation_history.csv"):
        """Initialize an empty history with a CSV file path."""
        self.file_path = Path(file_path)
        self._dataframe = pd.DataFrame(columns=self.COLUMNS)

    @property
    def dataframe(self) -> pd.DataFrame:
        """Return a copy of the calculation-history DataFrame."""
        return self._dataframe.copy()

    def add(self, calculation: Calculation) -> None:
        """Add a Calculation object to the history."""
        if not isinstance(calculation, Calculation):
            raise HistoryError(
                "History can only store Calculation objects."
            )

        new_row = pd.DataFrame([calculation.to_dict()])

        self._dataframe = pd.concat(
            [self._dataframe, new_row],
            ignore_index=True,
        )

    def clear(self) -> None:
        """Remove every calculation from history."""
        self._dataframe = pd.DataFrame(columns=self.COLUMNS)

    def save(self, file_path: str | None = None) -> None:
        """Save calculation history to a CSV file."""
        target_path = Path(file_path) if file_path else self.file_path

        try:
            target_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            self._dataframe.to_csv(target_path, index=False)
        except (OSError, PermissionError) as error:
            raise HistoryError(
                f"Unable to save history to {target_path}."
            ) from error

    def load(self, file_path: str | None = None) -> None:
        """Load calculation history from a CSV file."""
        target_path = Path(file_path) if file_path else self.file_path

        if not target_path.exists():
            raise HistoryError(
                f"History file does not exist: {target_path}"
            )

        try:
            loaded_dataframe = pd.read_csv(target_path)
        except (OSError, pd.errors.ParserError) as error:
            raise HistoryError(
                f"Unable to load history from {target_path}."
            ) from error

        missing_columns = set(self.COLUMNS) - set(
            loaded_dataframe.columns
        )

        if missing_columns:
            raise HistoryError(
                "History file is missing required columns."
            )

        self._dataframe = loaded_dataframe[self.COLUMNS].copy()

    def get_last(self) -> dict | None:
        """Return the latest history entry as a dictionary."""
        if self._dataframe.empty:
            return None

        return self._dataframe.iloc[-1].to_dict()

    def remove_last(self) -> dict | None:
        """Remove and return the latest history entry."""
        if self._dataframe.empty:
            return None

        last_entry = self._dataframe.iloc[-1].to_dict()
        self._dataframe = self._dataframe.iloc[:-1].reset_index(
            drop=True
        )

        return last_entry

    def restore(self, dataframe: pd.DataFrame) -> None:
        """Restore history from a previously saved DataFrame."""
        if not isinstance(dataframe, pd.DataFrame):
            raise HistoryError(
                "History can only be restored from a DataFrame."
            )

        missing_columns = set(self.COLUMNS) - set(dataframe.columns)

        if missing_columns:
            raise HistoryError(
                "DataFrame is missing required history columns."
            )

        self._dataframe = dataframe[self.COLUMNS].copy().reset_index(
            drop=True
        )

    def __len__(self) -> int:
        """Return the number of stored calculations."""
        return len(self._dataframe)

    def __str__(self) -> str:
        """Return a readable table of calculation history."""
        if self._dataframe.empty:
            return "No calculations in history."

        return self._dataframe.to_string(index=False)