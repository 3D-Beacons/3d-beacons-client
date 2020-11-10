#!/bin/sh

if [ "$DATABASE_TYPE" = "postgres" ]
then
    echo "Waiting for postgres to start (host=$DATABASE_HOST, port=$DATABASE_PORT)..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
fi

flask db upgrade
flask db migrate

exec "$@"
