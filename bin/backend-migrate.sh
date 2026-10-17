#!/bin/bash
set -e

docker compose exec heladeria_api python manage.py makemigrations && docker compose exec heladeria_api python manage.py migrate
