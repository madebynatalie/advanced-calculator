"""Arithmetic operation strategies and operation factory."""

from abc import ABC, abstractmethod
from math import pow

from app.exceptions import (
    DivisionByZeroError,
    InvalidOperationError,
    NegativeRootError,
)


class Operation(ABC):
    """Abstract base class for calculator operation strategies."""

    @abstractmethod
    def execute(self, first_number: float, second_number: float) -> float:
        """Perform an arithmetic operation and return the result."""


class AddOperation(Operation):
    """Strategy for addition."""

    def execute(self, first_number: float, second_number: float) -> float:
        return first_number + second_number


class SubtractOperation(Operation):
    """Strategy for subtraction."""

    def execute(self, first_number: float, second_number: float) -> float:
        return first_number - second_number


class MultiplyOperation(Operation):
    """Strategy for multiplication."""

    def execute(self, first_number: float, second_number: float) -> float:
        return first_number * second_number


class DivideOperation(Operation):
    """Strategy for division."""

    def execute(self, first_number: float, second_number: float) -> float:
        if second_number == 0:
            raise DivisionByZeroError("Cannot divide by zero.")

        return first_number / second_number


class PowerOperation(Operation):
    """Strategy for exponentiation."""

    def execute(self, first_number: float, second_number: float) -> float:
        return pow(first_number, second_number)


class RootOperation(Operation):
    """Strategy for calculating an nth root."""

    def execute(self, first_number: float, second_number: float) -> float:
        if second_number == 0:
            raise DivisionByZeroError("The root degree cannot be zero.")

        if first_number < 0 and second_number % 2 == 0:
            raise NegativeRootError(
                "Cannot calculate an even root of a negative number."
            )

        if first_number < 0:
            return -((-first_number) ** (1 / second_number))

        return first_number ** (1 / second_number)


class OperationFactory:
    """Factory that creates operation strategy objects."""

    _operations = {
        "add": AddOperation,
        "+": AddOperation,
        "subtract": SubtractOperation,
        "-": SubtractOperation,
        "multiply": MultiplyOperation,
        "*": MultiplyOperation,
        "divide": DivideOperation,
        "/": DivideOperation,
        "power": PowerOperation,
        "**": PowerOperation,
        "root": RootOperation,
    }

    @classmethod
    def create_operation(cls, operation_name: str) -> Operation:
        """Create and return an operation based on the provided name."""
        normalized_name = operation_name.strip().lower()

        operation_class = cls._operations.get(normalized_name)

        if operation_class is None:
            raise InvalidOperationError(
                f"Unsupported operation: {operation_name}"
            )

        return operation_class()