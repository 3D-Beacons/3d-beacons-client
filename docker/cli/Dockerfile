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

# install external dependencies (GEMMI)
# (do this early because it takes a long time and can be cached)
RUN apt-get update && apt-get install -y git cmake make g++
RUN git clone https://github.com/project-gemmi/gemmi.git && cd gemmi && cmake . && make
ENV GEMMI_BIN=/app/gemmi/gemmi

# copy python install files
COPY setup.cfg setup.py __version__.py bio3dbeacons/cli/requirements.txt ./

# install python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
RUN pip install -e .


# copy code
COPY bio3dbeacons bio3dbeacons

# copy schema
COPY resources resources

# copy Snakemake file and config
COPY .env Snakefile ./

# run cli command by default
ENTRYPOINT ["python3", "-m", "bio3dbeacons.cli"]
