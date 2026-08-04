FROM python:3.13-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY runserver.sh /scripts/runserver.sh
RUN chmod +x /scripts/runserver.sh

EXPOSE 8000

CMD [ "/scripts/runserver.sh" ]