"""Input validation helpers for the calculator application."""

import math

from app.exceptions import InvalidInputError


def validate_number(value: str | int | float) -> float:
    """
    Convert a value into a finite floating-point number.

    This function demonstrates both LBYL and EAFP error handling.
    """

    # LBYL: check for missing or blank input before conversion.
    if value is None:
        raise InvalidInputError("A number is required.")

    if isinstance(value, str) and not value.strip():
        raise InvalidInputError("A number is required.")

    # EAFP: attempt conversion and handle failure afterward.
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise InvalidInputError(
            f"Invalid number: {value}"
        ) from error

    if not math.isfinite(number):
        raise InvalidInputError("Number must be finite.")

    return number


def validate_operation_name(operation_name: str) -> str:
    """Validate and normalize an operation name."""

    if not isinstance(operation_name, str):
        raise InvalidInputError("Operation name must be text.")

    normalized_name = operation_name.strip().lower()

    if not normalized_name:
        raise InvalidInputError("Operation name is required.")

    return normalized_name