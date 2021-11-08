# Dockerfile

# To be run from the project root, eg:
# docker build -f docker/cli/Dockerfile .

# pull the official docker image
FROM python:3.7-slim

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY setup.cfg setup.py __version__.py ./
COPY bio3dbeacons/cli/requirements.txt ./

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
RUN pip install .

# copy project
COPY bio3dbeacons bio3dbeacons

# copy schema
COPY resources resources

# run cli command
ENTRYPOINT ["python3", "-m", "bio3dbeacons.cli"]
