"""Calculation model for the calculator application."""

from dataclasses import dataclass, field

from app.input_validators import (
    validate_number,
    validate_operation_name,
)
from app.operations import OperationFactory


@dataclass
class Calculation:
    """Represents a single calculator operation."""

    first_number: float
    second_number: float
    operation_name: str
    result: float = field(init=False)

    def __post_init__(self):
        """Validate inputs and compute the result."""

        self.first_number = validate_number(self.first_number)
        self.second_number = validate_number(self.second_number)
        self.operation_name = validate_operation_name(self.operation_name)

        operation = OperationFactory.create_operation(self.operation_name)

        self.result = operation.execute(
            self.first_number,
            self.second_number,
        )

    def to_dict(self):
        """Convert the calculation into a dictionary."""

        return {
            "First Number": self.first_number,
            "Second Number": self.second_number,
            "Operation": self.operation_name,
            "Result": self.result,
        }

    def __str__(self):
        """Return a readable representation."""

        return (
            f"{self.first_number} "
            f"{self.operation_name} "
            f"{self.second_number} "
            f"= {self.result}"
        )