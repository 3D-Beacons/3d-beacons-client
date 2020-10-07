FROM python:3.7-alpine

RUN apk update && apk add \
    gcc \
    g++ \
    linux-headers \
    postgresql-dev

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

RUN pip3 install -e .

EXPOSE 5000

ENTRYPOINT ["Docker/app/entrypoint.sh"]

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "bio3dbeacon:app.create_app()" ]
