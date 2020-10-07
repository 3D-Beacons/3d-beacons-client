#!/bin/sh

sleep 10

flask db upgrade
flask db migrate

exec "$@"
