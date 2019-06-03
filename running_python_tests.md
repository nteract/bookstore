# Running Python Tests

The project uses pytest to run Python tests and tox as a tool for running
tests in different environments.

## Setup Local development system

Using Python 3.6+, install the dev requirements:

```bash
pip install -r requirements-dev.txt
```

## Run Python tests

To run tests for a particular Python version (3.6 or 3.7):

```bash
tox -e py36  # or py37
```

This will run the tests and display coverage information.
