# pull the official docker image
FROM continuumio/miniconda3

# install Gemmi from conda-forge
RUN conda install -c conda-forge gemmi

# set work directory
WORKDIR /app

# Update pip, wheel and setuptools
RUN pip install --upgrade pip setuptools wheel

COPY . /app

# install CLI dependencies
RUN pip install .
