#!/bin/bash
set -e

echo "Esperando a PostgreSQL en $DB_HOST:5432..."
while ! nc -z $DB_HOST 5432; do
  sleep 0.5
done
echo "PostgreSQL listo"

python manage.py migrate --noinput

if [[ -n "${DJANGO_SU_NAME}" ]]; then
    echo "Configurando superusuario ${DJANGO_SU_NAME}..."
    python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()

username = '${DJANGO_SU_NAME}'
email = '${DJANGO_SU_EMAIL}'
password = '${DJANGO_SU_PASSWORD}'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.email = email
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f'Superusuario {username} actualizado')
except User.DoesNotExist:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superusuario {username} creado')
PYEOF
fi

python manage.py runserver 0.0.0.0:8000