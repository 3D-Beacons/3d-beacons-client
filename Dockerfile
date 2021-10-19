# pull the official docker image
FROM python:3.7-buster

# install build dependencies
RUN apt-get update && apt-get install -y git cmake make g++

# set work directory
WORKDIR /app

# install GEMMI
RUN git clone https://github.com/project-gemmi/gemmi.git && \
        cd gemmi && \
        cmake . && \
        make && \
        cd ..

COPY . /app

# install CLI dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install .
