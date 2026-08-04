"""Tests for arithmetic operation strategies and the operation factory."""

import pytest

from app.exceptions import (
    DivisionByZeroError,
    InvalidOperationError,
    NegativeRootError,
)
from app.operations import (
    AddOperation,
    DivideOperation,
    MultiplyOperation,
    OperationFactory,
    PowerOperation,
    RootOperation,
    SubtractOperation,
)


@pytest.mark.parametrize(
    "operation_class, first_number, second_number, expected_result",
    [
        (AddOperation, 5, 3, 8),
        (AddOperation, -5, 3, -2),
        (SubtractOperation, 10, 4, 6),
        (SubtractOperation, 4, 10, -6),
        (MultiplyOperation, 6, 7, 42),
        (MultiplyOperation, -3, 4, -12),
        (DivideOperation, 10, 2, 5),
        (DivideOperation, 7, 2, 3.5),
        (PowerOperation, 2, 3, 8),
        (PowerOperation, 5, 0, 1),
        (RootOperation, 9, 2, 3),
        (RootOperation, 27, 3, 3),
        (RootOperation, -27, 3, -3),
    ],
)
def test_operation_execute(
    operation_class,
    first_number,
    second_number,
    expected_result,
):
    """Test arithmetic operations with multiple valid inputs."""
    operation = operation_class()

    result = operation.execute(first_number, second_number)

    assert result == pytest.approx(expected_result)


@pytest.mark.parametrize(
    "operation_name, expected_class",
    [
        ("add", AddOperation),
        ("+", AddOperation),
        ("ADD", AddOperation),
        (" subtract ", SubtractOperation),
        ("-", SubtractOperation),
        ("multiply", MultiplyOperation),
        ("*", MultiplyOperation),
        ("divide", DivideOperation),
        ("/", DivideOperation),
        ("power", PowerOperation),
        ("**", PowerOperation),
        ("root", RootOperation),
    ],
)
def test_operation_factory_creates_correct_operation(
    operation_name,
    expected_class,
):
    """Test that the factory returns the correct operation strategy."""
    operation = OperationFactory.create_operation(operation_name)

    assert isinstance(operation, expected_class)


@pytest.mark.parametrize("second_number", [0, 0.0])
def test_divide_by_zero_raises_error(second_number):
    """Test that division by zero raises a custom exception."""
    operation = DivideOperation()

    with pytest.raises(
        DivisionByZeroError,
        match="Cannot divide by zero.",
    ):
        operation.execute(10, second_number)


@pytest.mark.parametrize("root_degree", [0, 0.0])
def test_zero_root_degree_raises_error(root_degree):
    """Test that a root degree of zero raises a custom exception."""
    operation = RootOperation()

    with pytest.raises(
        DivisionByZeroError,
        match="The root degree cannot be zero.",
    ):
        operation.execute(16, root_degree)


@pytest.mark.parametrize(
    "number, root_degree",
    [
        (-16, 2),
        (-81, 4),
    ],
)
def test_even_root_of_negative_number_raises_error(
    number,
    root_degree,
):
    """Test that even roots of negative numbers are rejected."""
    operation = RootOperation()

    with pytest.raises(
        NegativeRootError,
        match="Cannot calculate an even root of a negative number.",
    ):
        operation.execute(number, root_degree)


@pytest.mark.parametrize(
    "operation_name",
    [
        "modulus",
        "%",
        "",
        "unknown",
    ],
)
def test_operation_factory_rejects_invalid_operation(operation_name):
    """Test that unsupported operations raise a custom exception."""
    with pytest.raises(
        InvalidOperationError,
        match="Unsupported operation:",
    ):
        OperationFactory.create_operation(operation_name)