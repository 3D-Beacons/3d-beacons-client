# Dockerfile

# pull the official docker image
FROM python:3.7-slim

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY bio3dbeacons/api/requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY bio3dbeacons/api bio3dbeacons/api
