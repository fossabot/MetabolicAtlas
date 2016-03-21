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

All resources only accept GET unless otherwise noted.

| Resource                                                 | Notes |
|----------------------------------------------------------|-------|
| `/api/v1/models`                                         |       |
| `/api/v1/models/:model_id`                               |       |
| `/api/v1/authors`                                        |       |
| `/api/v1/authors/:author_id`                             |       |
| `/api/v1/reactions`                                      | 1     |
| `/api/v1/reactions/:reaction_id`                         |       |
| `/api/v1/reactions/:reaction_id/reactants`               |       |
| `/api/v1/reactions/:reaction_id/reactants/:component_id` |       |
| `/api/v1/reactions/:reaction_id/products`                |       |
| `/api/v1/reactions/:reaction_id/products/:component_id`  |       |
| `/api/v1/reaction_components`                            | 1     |
| `/api/v1/reaction_components/:component_id`              |       |

1: Use `limit` and `offset` as query parameters for pagination.


## `GET /api/v1/models`

Returns a list of models.

Example:

```bash
$ curl http://hostname/api/v1/models
{
  "models": [
    {
	  "model_id": 1,
	  "name": "Human Metabolic Reaction (HMR) 2.0 Database",
	  "short_name": "HMRdatabase",
	  "authors": [
	    {
		  "author_id": 1,
		  "given_name": "HMR",
		  "family_name": "Modeler",
		  "email": "hmr.modeler@example.com",
		  "organization": "ACME Modeling",
		  "models": [
            1
          ]
        }
      ]
    }
  ]
}

```


## `GET /api/v1/models/:model_id`

Returns a specific model.

Example:

```bash
$ curl http://hostname/api/v1/models/1
{
  "model_id": 1,
  "name": "Human Metabolic Reaction (HMR) 2.0 Database",
  "short_name": "HMRdatabase",
  "authors": [
    {
	  "author_id": 1,
	  "given_name": "HMR",
	  "family_name": "Modeler",
	  "email": "hmr.modeler@example.com",
	  "organization": "ACME Modeling",
	  "models": [
        1
      ]
    }
  ]
}
```


## `GET /api/v1/authors`

Returns a list of authors.

Example:

```bash
$ curl http://hostname/api/v1/authors
{
  "authors": [
    {
	  "author_id": 1,
	  "given_name": "HMR",
	  "family_name": "Modeler",
	  "email": "hmr.modeler@example.com",
	  "organization": "ACME Modeling",
	  "models": [
        1
      ]
    }
  ]
}
```


## `GET /api/v1/authors/:author_id`

Return a specific author.

Example:

```bash
$ curl http://hostname/api/v1/authors/1
{
  "author_id": 1,
  "given_name": "HMR",
  "family_name": "Modeler",
  "email": "hmr.modeler@example.com",
  "organization": "ACME Modeling",
  "models": [
    1
  ]
}
```


## `GET /api/v1/reactions`

Return a (truncated) list of reactions. Use `limit` and `offset` as
query parameters for pagination.

The new offset will be included in the response.

Example:

```bash
$ curl http://hostname/api/v1/reactions?limit=1&offset=1
{
  "limit": 1,
  "offset": 2,
  "reactions": [
    {
      "reaction_id": "R_HMR_3907",
      "name": null,
      "equation": "ethanol[c] + NADP+[c] => acetaldehyde[c] + H+[c] + NADPH[c]",
      "upper_bound": 1000.0,
      "lower_bound": 0.0,
      "objective_coefficient": 0.0,
      "sbo_term": 176,
      "products": [
        {
          "component_id": "M_m01249c",
          "formula": "C2H4O",
          "long_name": "acetaldehyde",
          "short_name": null,
          "organism": "Human",
          "type_code": 15
        },
        {
          "component_id": "M_m02039c",
          "formula": "H",
          "long_name": "H+",
          "short_name": null,
          "organism": "Human",
          "type_code": 15
        },
        {
          "component_id": "M_m02555c",
          "formula": "C21H30N7O17P3",
          "long_name": "NADPH",
          "short_name": null,
          "organism": "Human",
          "type_code": 15
        }
      ],
      "reactants": [
        {
          "component_id": "M_m01796c",
          "formula": "C2H6O",
          "long_name": "ethanol",
          "short_name": null,
          "organism": "Human",
          "type_code": 15
        },
        {
          "component_id": "M_m02554c",
          "formula": "C21H29N7O17P3",
          "long_name": "NADP+",
          "short_name": null,
          "organism": "Human",
          "type_code": 15
        }
      ]
    }
  ]
}
```


## `GET /api/v1/reactions/:reaction_id`

Return a specific reaction.

Example:

```bash
$ curl http://hostname/api/v1/reactions/R_HMR_4388
{
  "reaction_id": "R_HMR_3907",
  "name": null,
  "equation": "ethanol[c] + NADP+[c] => acetaldehyde[c] + H+[c] + NADPH[c]",
  "upper_bound": 1000.0,
  "lower_bound": 0.0,
  "objective_coefficient": 0.0,
  "sbo_term": 176,
  "products": [
    {
      "component_id": "M_m01249c",
      "formula": "C2H4O",
      "long_name": "acetaldehyde",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    },
    {
      "component_id": "M_m02039c",
      "formula": "H",
      "long_name": "H+",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    },
    {
      "component_id": "M_m02555c",
      "formula": "C21H30N7O17P3",
      "long_name": "NADPH",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    }
  ],
  "reactants": [
    {
      "component_id": "M_m01796c",
      "formula": "C2H6O",
      "long_name": "ethanol",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    },
    {
      "component_id": "M_m02554c",
      "formula": "C21H29N7O17P3",
      "long_name": "NADP+",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    }
  ]
}
```


## `GET /api/v1/reaction/:reaction_id/reactants`

Return a list of reactants for a specific reaction.

Example:

```bash
$ curl http://hostname/api/v1/reactions/R_HMR_3907/reactants
{
  "reactants": [
    {
      "component_id": "M_m01796c",
      "formula": "C2H6O",
      "long_name": "ethanol",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    },
    {
      "component_id": "M_m02554c",
      "formula": "C21H29N7O17P3",
      "long_name": "NADP+",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    }
  ]
}

```


## `GET /api/v1/reaction/:reaction_id/reactants/:component_id`

Return a specific reactant for a specific reaction.

Example:

```bash
$ curl http://hostname/api/v1/reaction/R_HMR_3907/reactants/M_m01796c
{
  "component_id": "M_m01796c",
  "formula": "C2H6O",
  "long_name": "ethanol",
  "short_name": null,
  "organism": "Human",
  "type_code": 15
}
```


## `GET /api/v1/reactions/:reaction_id/products`

Return a list of products for a specific reaction.

Example:

```bash
$ curl http://hostname/api/v1/reactions/R_HMR_3907/products
{
  "products": [
    {
      "component_id": "M_m01249c",
      "formula": "C2H4O",
      "long_name": "acetaldehyde",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    },
    {
      "component_id": "M_m02039c",
      "formula": "H",
      "long_name": "H+",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    },
    {
      "component_id": "M_m02555c",
      "formula": "C21H30N7O17P3",
      "long_name": "NADPH",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    }
  ]
}
```


## `GET /api/v1/reactions/:reaction_id/products/:component_id`

Return a specific product for a specific reaction.

Example:

```bash
$ curl http://hostname/api/v1/reactions/R_HMR_3907/products/M_m01249c
{
  "component_id": "M_m01249c",
  "formula": "C2H4O",
  "long_name": "acetaldehyde",
  "short_name": null,
  "organism": "Human",
  "type_code": 15
}
```


## `GET /api/v1/reaction_components`

Return a (truncated) list of reaction components. Use `limit` and
`offset` as query parameters for pagination.

The new offset will be included in the response.

Example:

```bash
$ curl http://hostname/api/v1/reaction_components?limit=1&offset=1
{
  "limit": 1,
  "offset": 2,
  "reaction_components": [
    {
      "component_id": "M_m02552c",
      "formula": "C21H28N7O14P2",
      "long_name": "NAD+",
      "short_name": null,
      "organism": "Human",
      "type_code": 15
    }
  ]
}
```


## `GET /api/v1/reaction_components/:component_id`

Return a specific reaction component.

Example:

```bash
$ curl http://hostname/api/v1/reaction_components/M_m02552c
{
  "component_id": "M_m02552c",
  "formula": "C21H28N7O14P2",
  "long_name": "NAD+",
  "short_name": null,
  "organism": "Human",
  "type_code": 15
}
```
