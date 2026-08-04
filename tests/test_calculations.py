"""Tests for Calculation."""

import pytest

from app.calculation import Calculation
from app.exceptions import (
    DivisionByZeroError,
    InvalidInputError,
    InvalidOperationError,
)


@pytest.mark.parametrize(
    "first, second, operation, expected",
    [
        (5, 3, "add", 8),
        (10, 5, "subtract", 5),
        (4, 6, "multiply", 24),
        (20, 4, "divide", 5),
        (2, 3, "power", 8),
        (9, 2, "root", 3),
    ],
)
def test_calculation_result(
    first,
    second,
    operation,
    expected,
):
    calculation = Calculation(
        first,
        second,
        operation,
    )

    assert calculation.result == pytest.approx(expected)


def test_to_dict():
    calculation = Calculation(5, 5, "add")

    assert calculation.to_dict() == {
        "First Number": 5.0,
        "Second Number": 5.0,
        "Operation": "add",
        "Result": 10.0,
    }


def test_string_representation():
    calculation = Calculation(5, 5, "add")

    assert str(calculation) == "5.0 add 5.0 = 10.0"


def test_invalid_operation():
    with pytest.raises(InvalidOperationError):
        Calculation(5, 5, "banana")


def test_invalid_number():
    with pytest.raises(InvalidInputError):
        Calculation("hello", 5, "add")


def test_division_by_zero():
    with pytest.raises(DivisionByZeroError):
        Calculation(10, 0, "divide")