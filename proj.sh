# To make sure docker-compose is in the path
export PATH=$PATH:/usr/local/bin

function build-stack {
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml build $@
}

function start-stack {
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml up -d
}

function stop-stack {
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml kill
}

function clean-stack {
  docker stop $(docker ps -a -q) || true
  docker rm $(docker ps -a -q) || true
  docker volume prune --force || true
  # The line below was not removing the db container properly
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml down
  docker volume prune -f
}

function logs {
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml logs -f $@
}

function db-import {
  docker exec -i db psql -U postgres < $1
}

function db-make-migrations {
  docker exec backend python manage.py makemigrations api
}

function db-migrate {
  docker exec backend python manage.py migrate --database=$@
}

echo -e "Available commands:
\tbuild-stack [options for dev instance only]
\tstart-stack
\tstop-stack
\tclean-stack
\tlogs [container]
\tdb-import [database]
\tdb-make-migrations
\tdb-migrate [database]"

if [ "$1" != 'production' ] ; then
  export MET_ATLAS_VERSION=local
  echo 'Sourced for LOCALHOST'
else
  export MET_ATLAS_VERSION=prod
  echo 'Sourced for PRODUCTION'
fi
