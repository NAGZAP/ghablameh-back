FROM python:3.11

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput
RUN chmod +x ./docker/docker-entrypoint.sh

EXPOSE 8000