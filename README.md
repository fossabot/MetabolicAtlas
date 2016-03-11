# HMA Backend Prototype

## About

This is a prototype for deploying the backend part of the Human
Metabolic Atlas using Docker. PostgreSQL for storage, nginx as proxy,
and gunicorn to serve the Flask app.

Structure and inspiration taken from [0].

[0] https://realpython.com/blog/python/dockerizing-flask-with-compose-and-machine-from-localhost-to-the-cloud/


## Prerequisites

* [Docker](https://docs.docker.com/engine/) (v1.9.0)
* [Docker Compose](https://docs.docker.com/compose/) (v1.5.0)
* [Docker Machine](https://docs.docker.com/machine/) (v0.5.0)
* libpq-dev (needed for psycopg2)


## Running

In the root directory, execute the following:

```bash
$ docker-machine create -d virtualbox dev
$ eval "$(docker-machine env dev)"
$ docker-compose build
$ docker-compose up -d
$ docker-compose run web /usr/local/bin/python create_db.py
$ docker-compose run web /usr/local/bin/python populate_db.py
```

Once everything is up, the application is available on port 80 on the
virtual machine (use `docker-machine ip` to get the IP address).

E.g.:

```bash
$ curl -v `docker-machine ip dev`
```
