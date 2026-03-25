#!/bin/bash

if [ ! -f manage.py ]; then
    django-admin startproject app .
fi

sleep 2

python manage.py makemigrations
python manage.py migrate --noinput

if [[ ! -z "${DJANGO_SU_NAME}" ]]; then
    echo "from django.contrib.auth.models import User; User.objects.filter(username='${DJANGO_SU_NAME}').exists() or User.objects.create_superuser('${DJANGO_SU_NAME}', '${DJANGO_SU_EMAIL}', '${DJANGO_SU_PASSWORD}')" | python manage.py shell
    echo "Verificando superusuario..."
    echo "from django.contrib.auth.models import User; u = User.objects.get(username='${DJANGO_SU_NAME}'); u.set_password('${DJANGO_SU_PASSWORD}'); u.save(); print('Superusuario ${DJANGO_SU_NAME} configurado correctamente')" | python manage.py shell
fi

python manage.py runserver 0.0.0.0:8000