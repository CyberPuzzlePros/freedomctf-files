FROM python:3.8

WORKDIR /code

RUN pip install gunicorn flask

COPY . .

CMD ["./gunicorn_starter.sh"]