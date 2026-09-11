#!/bin/sh
set -eu

cd /app/python/src
flask --app run:app db upgrade
flask --app run:app seed-demo
exec waitress-serve --host=0.0.0.0 --port="${PORT:-8080}" run:app