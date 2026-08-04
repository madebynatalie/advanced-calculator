"""Tests for calculator input validation."""

import pytest

from app.exceptions import InvalidInputError
from app.input_validators import (
    validate_number,
    validate_operation_name,
)


@pytest.mark.parametrize(
    "value, expected_result",
    [
        ("5", 5.0),
        ("  7.5  ", 7.5),
        ("-3", -3.0),
        (10, 10.0),
        (2.5, 2.5),
        ("1e3", 1000.0),
    ],
)
def test_validate_number_accepts_valid_values(value, expected_result):
    """Test that valid numeric values are converted to floats."""
    assert validate_number(value) == pytest.approx(expected_result)


@pytest.mark.parametrize(
    "value, expected_message",
    [
        (None, "A number is required."),
        ("", "A number is required."),
        ("   ", "A number is required."),
        ("hello", "Invalid number: hello"),
        ([], "Invalid number: []"),
        ("nan", "Number must be finite."),
        ("inf", "Number must be finite."),
        ("-inf", "Number must be finite."),
    ],
)
def test_validate_number_rejects_invalid_values(
    value,
    expected_message,
):
    """Test that invalid numeric values raise custom errors."""
    with pytest.raises(
        InvalidInputError,
        match=expected_message.replace(
            "[",
            r"\[",
        ).replace(
            "]",
            r"\]",
        ),
    ):
        validate_number(value)


@pytest.mark.parametrize(
    "operation_name, expected_result",
    [
        ("add", "add"),
        (" ADD ", "add"),
        ("+", "+"),
        ("Root", "root"),
    ],
)
def test_validate_operation_name_accepts_valid_text(
    operation_name,
    expected_result,
):
    """Test operation-name normalization."""
    assert validate_operation_name(operation_name) == expected_result


@pytest.mark.parametrize(
    "operation_name, expected_message",
    [
        (None, "Operation name must be text."),
        (5, "Operation name must be text."),
        ("", "Operation name is required."),
        ("   ", "Operation name is required."),
    ],
)
def test_validate_operation_name_rejects_invalid_values(
    operation_name,
    expected_message,
):
    """Test invalid operation names."""
    with pytest.raises(
        InvalidInputError,
        match=expected_message,
    ):
        validate_operation_name(operation_name)