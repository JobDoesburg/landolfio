# Landolfio

## Getting Started

To get started, follow these steps:

1. Install [Python 3.9+](https://www.python.org/) and [poetry](https://python-poetry.org/docs/#installation).
2. Clone this repository.
3. Run `poetry install` to install all dependencies into the virtual
   environment.
4. Run `poetry run pre-commit install` to install the pre-commit hooks.
5. Run `poetry shell` to enter the virtual environment.
6. Run `cd website` to navigate to the folder containing `manage.py`.
7. Run `python ./manage.py migrate` to initialize the database.
8. Run `python ./manage.py runserver` to start the local testing server.

### Testing

To test Landolfio, follow these steps:

1. Run `poetry shell` to enter the virtual environment.
2. Run `cd website` to navigate to the folder containing `manage.py`.
3. Run `python ./manage.py test`
