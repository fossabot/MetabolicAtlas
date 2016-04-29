# HMA Backend Prototype

## About

This is a prototype for deploying the backend part of the Human
Metabolic Atlas using Docker. PostgreSQL for storage, nginx as proxy,
and gunicorn to serve the Flask app.

Structure and inspiration taken from [0].

[0] https://realpython.com/blog/python/dockerizing-flask-with-compose-and-machine-from-localhost-to-the-cloud/


## Prerequisites

* [VirtualBox](https://www.virtualbox.org/)
* [Docker](https://docs.docker.com/engine/) (v1.9.0)
* [Docker Compose](https://docs.docker.com/compose/) (v1.5.0)
* [Docker Machine](https://docs.docker.com/machine/) (v0.5.0)
* libpq-dev (needed for psycopg2)


## Setting up

First, we'll need to download the additional data sources:

```bash
$ wget http://www.metabolicatlas.org/assets/hmr/HMRcollection2_00.xml-f0de1f951d16f78abf131cece19f8af7.zip
$ wget http://v14.proteinatlas.org/download/normal_tissue.csv.zip
$ wget http://v14.proteinatlas.org/download/transcript_rna_tissue.tsv.zip
```

Unzip the files and place them in the `hma_backend/import/`
folder. You will also need a file that maps ENSGIDs to HGNC symbols
(which will be used as short_name for the ReactionComponents). Place
it in the same folder.

Next step is to spin up the containers. In the root directory, execute
the following:

```bash
$ docker-machine create -d virtualbox dev
$ eval "$(docker-machine env dev)"
$ docker-compose build
$ docker-compose up -d
$ psql -h `docker-machine ip dev` -p 5432 -U postgres --password -d hma -c "create extension pg_trgm;"
$ docker-compose run --rm backend /usr/local/bin/python create_db.py
```

After that, we'll populate the database. This is done in three steps.


### First step - Import GEM file

```bash
$ docker-compose run --rm backend /usr/local/bin/python populate_db.py import/HMRdatabase2_00.xml import/normal_tissue.csv
```


### Second step - Import HPA expression data

```bash
$ source dev_env.sh # this let's us connect to the db directly
$ cd hma_backend
# this takes some time
$ python generate_abp_expr_csv.py import/HMRdatabase2_00.xml \
    import/normal_tissue.csv
$ cat abp_expr_*.csv > abp.expr.csv && rm abp_expr_*.csv
# this takes even longer time
$ python generate_rnaseq_expr_csv.py import/HMRdatabase2_00.xml \
    import/transcript_rna_tissue.tsv
$ cat rnaseq_expr_*.csv > rnaseq_expr.csv && rm rnaseq_expr_*.csv
```

Next, we load the CSV files into the database:

```bash
$ psql -h `docker-machine ip dev` -p 5432 -U postgres --password hma \
    -c "\copy expression_data from abp_expr.csv' delimiter ',' csv;"
$ psql -h `docker-machine ip dev` -p 5432 -U postgres --password hma \
    -c "\copy expression_data from 'rnaseq_expr.csv' delimiter ',' csv;"
```


### Third step - Update reaction components with new data

The expression data that we loaded contains information that we want
to include in the reaction components in the database (`short_name`
and `component_type`). We run this to make the updates:

```bash
$ docker-compose run --rm backend /usr/local/bin/python \
    update_component_info.py import/HMRdatabase2_00.xml
$ docker-compose run --rm backend /usr/local/bin/python \
	add_short_names.py import/ensembl78_hgnc_symbol.hsapiens.tab
```


## Usage

Once everything is up, the backend application is available on port 80
on the virtual machine (use `docker-machine ip` to get the IP
address).

E.g.:

```bash
$ curl -v `docker-machine ip dev`
```
