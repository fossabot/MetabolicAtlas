# Table of Contents

1. [About](#about)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [API](#api)
5. [Examples](#examples)


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


# Examples

To get an idea of what the backend can provide, here are some example
queries to get you started:

## List interaction partners

Interaction partners are reaction components that are part of the same
reaction. Here are three different examples to give you an idea of the
size difference in the responses:

```bash
# 91 lines
$ curl http://<server>/api/v1/reaction_components/E_2571/interaction_partners
# 569 lines
$ curl http://<server>/api/v1/reaction_components/E_3125/interaction_partners
# 5966 lines
$ curl http://<server>/api/v1/reaction_components/M_m02040s/interaction_partners
```

## Get connected metabolites

Given an enzyme with an ENSEMBL gene identifier, we can get a list of
the metabolites that occur in the reactions that the enzyme is a part
of. The response can also include expression data, if the query
parameter `include_expressions` is set to `true`. E.g.:

```bash
# expressions as a link to another resource, 96 lines
$ curl http://<server>/api/v1/enzymes/ENSG00000164303/connected_metabolites
# expressions as a list, 2320 lines
$ curl http://<server>/api/v1/enzymes/ENSG00000164303/connected_metabolites?include_expressions=true
```
