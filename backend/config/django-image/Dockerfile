FROM python:3.14.3

RUN apt-get update && apt-get install python3-dev libgdal-dev graphviz graphviz-dev -y --force-yes

WORKDIR /usr/src/app 

RUN pip install --upgrade pip && pip install --upgrade setuptools

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN mkdir /scripts
COPY runserver.sh /scripts/runserver.sh
RUN chmod +x /scripts/runserver.sh

CMD [ "/scripts/runserver.sh" ]

#CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]