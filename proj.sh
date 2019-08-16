# To make sure docker-compose is in the path
export PATH=$PATH:/usr/local/bin

function build-stack {
  if [ "$METATLASPROD" = true ] ; then
    docker-compose -f docker-compose.yml -f docker-compose-prod.yml build $@
  else
    docker-compose -f docker-compose.yml -f docker-compose-local.yml build
  fi
}

function start-stack {
  if [ "$METATLASPROD" = true ] ; then
    docker-compose -f docker-compose.yml -f docker-compose-prod.yml up -d
  else
    docker-compose -f docker-compose.yml -f docker-compose-local.yml up -d
  fi
}

function stop-stack {
  if [ "$METATLASPROD" = true ] ; then
    docker-compose -f docker-compose.yml -f docker-compose-prod.yml kill
  else
    docker-compose -f docker-compose.yml -f docker-compose-local.yml kill
  fi
}

function clean-stack {
  docker stop $(docker ps -a -q) || true
  docker rm $(docker ps -a -q) || true
  docker volume prune --force || true
  # The code below was not removing the db container properly
  if [ "$METATLASPROD" = true ] ; then
    docker-compose -f docker-compose.yml -f docker-compose-prod.yml down
  else
    docker-compose -f docker-compose.yml -f docker-compose-local.yml down
  fi
  docker volume prune -f
}

function logs {
  if [ "$METATLASPROD" = true ] ; then
    docker-compose -f docker-compose.yml -f docker-compose-prod.yml logs -f $@
  else
    docker-compose -f docker-compose.yml -f docker-compose-local.yml logs -f $@
  fi
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
  export METATLASPROD=false
  echo 'Sourced for LOCALHOST'
else
  export METATLASPROD=true
  echo 'Sourced for PRODUCTION'
fi
