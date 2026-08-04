# Advanced Calculator

A command-line calculator built in Python using object-oriented programming, design patterns, pandas, and pytest.

## Features

- Add, subtract, multiply, divide, power, and root operations
- REPL command-line interface
- Calculation history
- Save and load history with pandas
- Undo and redo
- Environment variable configuration
- Factory, Strategy, Facade, Observer, and Memento design patterns
- Automated testing with pytest
- GitHub Actions CI
- 100% test coverage

## Installation

```bash
pip install -r requirements.txt
```

## Run the Calculator

```bash
python -m app.calculator_repl
```

## Run Tests

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-branch
```

## Commands

```
add
subtract
multiply
divide
power
root
history
undo
redo
save
load
clear
help
exit
```
