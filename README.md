# Metabolic Atlas
Welcome to the codebase for the Metabolic Atlas project.

The front-end uses [Vue.js](https://vuejs.org), with help of [Vue CLI](https://cli.vuejs.org/). The backend uses [Django REST framework](http://www.django-rest-framework.org) with [PostgreSQL](https://www.postgresql.org) as the database.  
To learn more about the project, including database setup, support for multiple databases, and testing, please visit the [wiki](https://github.com/SysBioChalmers/MetabolicAtlas/wiki).

## Prerequisites
Docker, along with docker-compose, is used to manage the dependencies of this project. To install Docker, download it from [here](https://www.docker.com/products/docker) (docker-compose should also be installed).

## Get started

Add a `postgres.env` file based on the `postgres.env.sample` file:
```bash
cp postgres.env.sample postgres.env
```
and modify the `postgres.env`. To load the list of helper commands:
```bash
source proj.sh
```

Build and run the project:
```bash
build-stack
start-stack
```

The frontend should be available at: `http://localhost/` and the backend should be available at: `http://localhost/api/` via Swagger. If you encounter any problems try running `restart-stack`, or look at the logs `logs backend` / `logs frontend`

### All helper commands

* To bootstrap the project: `build-stack`
* To run the project: `start-stack`
* To display real-time logs: `logs [container-name: frontend/backend/nginx/db]`
* To stop the project: `stop-stack`
* To import a database: `db-import [database-file.db]`
* To create new migration files: `db-make-migrations`
* To run a database migration: `db-migrate [database]`
