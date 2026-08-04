"""Custom exceptions used throughout the calculator application."""


class CalculatorError(Exception):
    """Base exception for calculator-related errors."""


class InvalidOperationError(CalculatorError):
    """Raised when the requested calculator operation is unsupported."""


class InvalidInputError(CalculatorError):
    """Raised when user input cannot be converted into valid numbers."""


class DivisionByZeroError(CalculatorError):
    """Raised when division by zero is attempted."""


class NegativeRootError(CalculatorError):
    """Raised when an even root of a negative number is attempted."""


class ConfigurationError(CalculatorError):
    """Raised when calculator configuration values are invalid."""


class HistoryError(CalculatorError):
    """Raised when calculation history cannot be saved or loaded."""


class UndoRedoError(CalculatorError):
    """Raised when an undo or redo action cannot be completed."""