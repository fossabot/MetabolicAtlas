# Table of Contents

1. [About](#about)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [API](#api)


# About

This is a REST backend for accessing metabolic models and their
components. This application is a part of the Human Metabolic Atlas.


# Prerequisites

* Python 3
* A PostgreSQL database

Set up a virtual environment and install dependencies:

```bash
$ pyvenv /path/to/hma_backend_venv
$ source /path/to/hma_backend_venv/bin/activate
$ pip install -r requirements.txt
```

## Testing

To run the tests, `coverage` must be installed:

```bash
$ pip install -r requirements_testing.txt
```


# Configuration

The application is configured using environment variables:

| Name         | Description                  |
|--------------|------------------------------|
| DB_USER      | PostgreSQL user              |
| DB_PASS      | Password for PostgreSQL user |
| DB_NAME      | Database name                |
| DB_SERVICE   | Database hostname/IP         |
| DB_PORT      | Database port                |
| FLASK_CONFIG | Application environment      |


# Running

The default `make` target starts up the application in a development
environment.

Tests are executed by running `make test`.


# API

A definition of the API is available at `/api/v1/spec`, use
[Swagger UI](https://github.com/swagger-api/swagger-ui) to explore it:

```bash
$ git clone https://github.com/swagger-api/swagger-ui.git
$ cd swagger-ui/dist
$ vim index.html # set $url to "http://<hma server>/api/v1/spec"
$ python3 -m http.server
```

Then open up [http://localhost:8000](http://localhost:8000) in your
browser.
