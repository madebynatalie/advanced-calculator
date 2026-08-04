"""Observer pattern implementation for calculator events."""

from abc import ABC, abstractmethod


class Observer(ABC):
    """Abstract observer."""

    @abstractmethod
    def update(self, calculator):
        """React to a calculator event."""


class LoggingObserver(Observer):
    """Simple observer used for logging."""

    def update(self, calculator):
        print(
            f"Calculation history now contains "
            f"{calculator.history_count} calculations."
        )


class AutoSaveObserver(Observer):
    """Automatically save history when notified."""

    def update(self, calculator):
        if calculator.config.auto_save:
            calculator.save_history()