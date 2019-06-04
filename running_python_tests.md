# Running Python Tests

The project uses pytest to run Python tests and tox as a tool for running
tests in different environments.

## Setup Local development system

Using Python 3.6+, install the dev requirements:

```bash
pip install -r requirements-dev.txt
```

## Run Python tests

**Important:** We recommend using tox for running tests locally.
Please deactivate any conda environments before running
tests using tox. Failure to do so may corrupt your virtual environments.

To run tests for a particular Python version (3.6 or 3.7):

```bash
tox -e py36  # or py37
```

This will run the tests and display coverage information.

## Run linters

```bash
tox -e flake8
tox -e black
```

## Run type checking

```bash
tox -e mypy
```

## Run All Tests and Checks

```bash
tox
```
