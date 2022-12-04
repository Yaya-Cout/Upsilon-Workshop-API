# Upsilon Workshop API

This is the API for the Upsilon Workshop. It is a REST API that allows you to
control the Upsilon workshop.

## Installation

To install the API, you need to have a working installation of Python 3.9 or
higher. You also need to have a working installation of pip.

### Virtualenv (optional)

It is recommended to use a virtualenv to install the API. This will allow you
to install the API without affecting your system's Python installation.

To create a virtualenv, run:

```bash
pip install virtualenv
virtualenv env
```

To activate the virtualenv, run:

```bash
source env/bin/activate
```

### Dependencies

To start, you need to install the dependencies. You can do this by running:

```bash
python -m pip install -r requirements.txt
```

### Database

Once you have installed the dependencies, you have to initialize the database.

```bash
python manage.py makemigrations workshop
python manage.py migrate workshop
```

### Creating a superuser

To create a superuser, run:

```bash
python manage.py createsuperuser
```

## Running the server

To run the server, you can use the following command:

```bash
python manage.py runserver
```

This will start the server on port 8000. You can change this by writing:

```bash
python manage.py runserver 8080
```

## Running the tests

To run the tests, you can use the following command:

```bash
python manage.py test
```

If you want to use pytest, ensure that you have `pytest-django` plugin installed
and run the following command:

```bash
pytest
```

You can integrate pytest with your IDE (tested with VSCode) by adding Pytest
configuration in your tests' configuration.

## Contributing

If you want to contribute to this project, you can do so by forking the
repository and creating a pull request. If you want to discuss something, you
can create an issue.
