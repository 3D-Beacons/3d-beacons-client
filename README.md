# 3D-Beacons Client

This is an implementation of 3D-Beacons client which provides various tools and infrastructure to make local structural models available to the [3D-Beacons](https://github.com/3D-Beacons/3D-Beacons/wiki) network.

More about 3D-Beacons can be found in the [WikiPages](https://github.com/3D-Beacons/3D-Beacons/wiki)

## Requirements

The 3D-Beacons Client has been made available as a series of docker containers, so the following software must be available:

- [docker-compose](https://docs.docker.com/compose/install/)
- [python3](https://www.python.org/downloads/)

## Quick Start

Download the code

```
$ git clone git@github.com:3D-Beacons/3d-beacons-client.git
$ cd 3d-beacons-client
```

Prepare the model data directories and files - every model needs a PDB/CIF file and a JSON file
(containing metadata about how this model maps to a UniProt entry).

```
$ mkdir -p ./data/{pdb,cif,metadata,index}
$ cp model001.pdb ./data/pdb/
$ cat model001.json
{
  "mappingAccession": "P38398",
  "mappingAccessionType": "uniprot",
  "start": 1,
  "end": 103,
  "modelCategory": "TEMPLATE-BASED",
  "modelType": "single"
}
$ cp model001.json ./data/metadata/
```

The `./data` directory should now look something like this (the model file has been given a more realistic name):

```
data
├── cif
├── index
├── metadata
│   └── P38398_1jm7.1.A_1_103.json
└── pdb
    └── P38398_1jm7.1.A_1_103.pdb
```

Now we need to setup the local environment - copy over the example and update `MONGO_PASSWORD` and `PROVIDER`.

```
cp .env.example .env
vim .env
```

We can now start up the docker containers.

Note: the following may take a few minutes the first time it is run
(the resulting images are cached by default, so they should only need to be built once).

```
docker-compose up -d
```

You should now be able to access the API documentation by directing a web browser at http://localhost:8000/docs

Process the model PDB files:

```
$ docker-compose exec cli snakemake --cores=2
```

The `./data` directory should now look like:

```
data
├── cif
│   └── P38398_1jm7.1.A_1_103.cif
├── index
│   ├── P38398_1jm7.1.A_1_103.json
│   └── P38398_1jm7.1.A_1_103.json.loaded
├── metadata
│   └── P38398_1jm7.1.A_1_103.json
└── pdb
    └── P38398_1jm7.1.A_1_103.pdb
```

We can now search for this model via the API:

```
$ curl -X 'GET' \
  'http://localhost:8000/uniprot/summary/P38398.json' \
  -H 'accept: application/json'

{"uniprot_entry":{"ac":"P38398","id":"BRCA1_HUMAN"},"structures":[{"model_identifier":"P38398_1jm7.1.A_1_103","model_category":"TEMPLATE-BASED","model_url":"localhost/static/cif/P38398_1jm7.1.A_1_103.cif","provider":"GENOME3D","uniprot_start":1,"uniprot_end":103,"model_format":"MMCIF"}]}
```

## Running CLI commands manually

The Snakemake workflow has been included for convenience, but it is possible
to run the individual steps outside of Snakemake, and outside of the docker
container entirely if desired.

Running steps inside docker (recommended)

- Pros: nothing to install
- Cons: docker adds a layer of complexity (eg different hosts and data directories)

```
# create a shortcut to run the CLI tool inside docker container
$ alias 3dbeacons-cli-docker="docker-compose exec cli 3dbeacons-cli"

# convert all PDB files to CIF files
$ 3dbeacons-cli-docker convert-pdb2cif -i ./data/pdb/ -o ./data/cif/

# prepare metadata for every CIF file
$ ls ./data/cif/model001.cif          # this file was generated in the step above
$ cat ./data/metadata/model001.json   # you need to generate this file yourself
{
    "mappingAccession": "P38398",
    "mappingAccessionType": "uniprot",
    "start": 1,
    "end": 103,
    "modelCategory": "TEMPLATE-BASED",
    "modelType": "single"
}

# create index JSON from CIF
$ 3dbeacons-cli-docker convert-cif2index \
  -ic ./data/cif/ -im ./data/metadata/ \
  -o ./data/index/

# load JSON to local database
# IMPORTANT: notice that the host from inside docker is 'mongodb'
$ 3dbeacons-cli-docker load-index \
  -i ./data/index/ \
  -h mongodb://MONGO_USER:MONGO_PASSWORD@mongodb:27017

# validate JSON
$ 3dbeacons-cli-docker validate-index \
  -i ./data/index/
```

Running CLI commands outside of docker

- Pros: one fewer layers to consider
- Cons: requires more manual installation

```
# create a virtual environment
$ python3 -m venv venv

# use the virtual environment
$ . venv/bin/activate

# make the all the installation libraries are up to date
$ pip install --upgrade pip setuptools wheel

# install the dependencies for this project
$ pip install -r bio3dbeacons/cli/requirements.txt

# install the CLI script
$ pip install -e .

# run the CLI tool
$ 3dbeacons-cli
Usage: 3dbeacons-cli [OPTIONS] COMMAND [ARGS]...

  CLI application for 3D Beacons utilities

Options:
  --help  Show this message and exit.

Commands:
  convert-cif2json
  convert-pdb2cif
  load-json
  validate-index
```

You will also need to install [GEMMI software](https://gemmi.readthedocs.io/en/latest/install.html).
The instuctions will vary depending on your operating system, but it will look something like:

```
apt-get update && apt-get install -y git cmake make g++
git clone https://github.com/project-gemmi/gemmi.git && cd gemmi && cmake . && make
export GEMMI_BIN=$PWD/gemmi
```

---

## Components

### CLI tools

These are Python based commands which provides utilities for easily hosting the models. Below are the utilities available.

#### 1. PDB to CIF conversion

The models in PDB can be converted to CIF files using this tool. It uses [Gemmi](https://gemmi.readthedocs.io/en/latest/install.html#gemmi-program) command-line program for the conversion. The tool accepts a single PDB file or a directory containing PDB files and generates the CIF files accordingly.

#### 2. CIF to JSON conversion

An index JSON is required for each model which can be loaded to the Mongo DB for keeping metadata for the model and exposing it via API. This index JSON can be created from the model CIF and a mandatory metadata JSON which contains the remaining metadata which is not available in CIF. This uses [Gemmi CIF Parser](https://gemmi.readthedocs.io/en/latest/cif.html) to get data from the CIF file. The tool will parse CIF file and metadata JSON and then merge both of them to create the index JSON. If there is already an existing value in CIF file, this will be overridden by the field in metadata JSON.

For example, if there is a field in CIF `_exptl.method` which maps to `experimentalMethod` in index JSON, this will be overwritten if there is an `experimentalMethod` field in metadata JSON.

The field mappings in CIF file to index JSON is configured via `cif_json_mapping` section in `bio3dbeacons/config/conf.ini`

**NOTE:** The metadata JSON should be named the same as that of CIF file except the file extension.

Below is an example metadata JSON with all mandatory fields. Description for each of these fields are available in `resources/schema.json`

```
{
"mappingAccession": "P38398",
"mappingAccessionType": "uniprot",
"start": 1,
"end": 103,
"modelCategory": "TEMPLATE-BASED",
"modelType": "single"
}
```

The tool can accept a single CIF and metadata JSON or directories containing the files and will generate the index JSONs accordingly.

#### 3. Mongo load

This tool can be used to load index JSON documents to Mongo DB to store the model metadata. This can accept a single JSON document or a directory containing the documents and use the DB url passed as the argument to load them into the database with an option of giving the batch size of documents to be loaded at once.

**NOTE:** The tool always upserts (insert if not present, else update) the documents.

#### 4. Validate index JSON

All the index JSON documents must be compliant with the schema provided in `resources/schema.json`. This tool can be used to run the validation of a single JSON or a directory against this schema before loading them to the database.

### Mongo DB database

[Mongo DB](https://www.mongodb.com/) is used to store the model metadata which will be used by the API to expose it via service endpoints. By using Mongo's document data model, the model metadata in the form of JSON documents can be loaded to Mongo DB and can be queried in the very fastest and efficient way to present it to the users.

### RESTful API

The client also provides a RESTful API to expose the model metadata to users as per the OpenAPI 3 specifications hosted in [SwaggerHub](https://app.swaggerhub.com/apis/3dbeacons/3D-Beacons/1.0.0). This is built on [FastAPI](https://fastapi.tiangolo.com/) web framework based on Python 3.6+ standards.

### File server

The RESTful API service is backed by an [NGINX](https://www.nginx.com/) proxy which also acts as a static file server to serve the model files like CIF and PDB.

## Developing

### Local development

For local development, please follow the below instructions.

##### Set the environment variables

Make sure the environment has been set up correctly (`.env`)

```
MONGO_USERNAME=<username> # username for MongoDB
MONGO_PASSWORD=<password> # password for MongoDB
PROVIDER=<provider> # Same as set in earlier section
MONGO_DB_HOST=localhost:27017 # Mongo DB docker compose service
MODEL_FORMAT=<format> # Same as set in earlier section
ASSETS_URL=localhost/static # NGINX docker compose service
```

Note: if you make any changes to this file _after_ the docker containers have been built, then you will need to rebuild the `cli` containers in order to be able to see those changes within `docker-compose`:

```
docker-compose up --detach --build cli
```

##### Start the necessary services

```
$ docker compose up --build
```

The above docker compose command will start API, Mongo DB and NGINX services defined in `docker-compose.yml` file. Each of these services uses environment variables provided in `docker-compose.yml` for its configuration.

Once the docker compose command is executed and services started, API docs can be accessed using [http://localhost/docs](http://localhost/docs). This is the default SwaggerHub style document auto generated by FastAPI.
Also Mongo DB can be accessed using [Mongo Shell](https://docs.mongodb.com/mongodb-shell/#mongodb-binary-bin.mongosh) using the below command,

```
$ mongosh mongodb://<MONGO_USERNAME>:<MONGO_PASSWORD>@localhost:27017
```

**NOTE**: If you check the NGINX service in `docker-compose.yml`, `/var/www/static` directory in NGINX is mounted with `data` directory in the project root. This is where the model files need to be kept for serving via file server. API is configured to expect CIF files to be kept in `data/cif` and PDB files to be in `data/pdb` directories. If another directory is used (which obvioulsly in most cases), replace `./data` in `docker-compose.yml` with the proper path where your model files are present. But make sure you still keep them in `cif` and `pdb` subdirectories accordingly.

##### Develop API locally

The docker compose command will start an API service inside the docker container. This may not be a good option to continously test and develop your services. To develop the API locally, use the below commands.

```
# Create a new Python (3.6+) virtual environment
$ python3 -m venv venv

# activate the environment
$ source venv/bin/activate

# Install the dependencies
$ pip install -r bio3dbeacons/api/requirements.txt
```

The above commands will create a new Python virtual environment and install the dependencies required to run the API.

Alternatively, environment can be managed very easily using [Anaconda](https://docs.anaconda.com/) as well. Use below commands to manage via conda.

```
$ conda create -n beacons_env -c conda-forge python=3.7 gemmi
$ conda activate beacons_env
```

The above commands will create a new conda environment `beacons_env` with Python version 3.7 along with the Gemmi program which is later used by CLI.

To use environment variables, API is using a python package `python-dotenv` which is a convenient way of keeping the variables in a `.env` file in the project directory.

Now that dependencies and environment variables are available, run the API locally using [uvicorn](https://www.uvicorn.org/) which is a lightning fast ASGI server implementation. This is already installed using the `pip` command executed before.

```
uvicorn bio3dbeacons.api.main:app --reload
```

Now access the local API docs using [http://localhost:8000/docs](http://localhost:8000/docs). The server will keep monitoring the files and reloads the instance without the need for restarting the server after making any code changes.

**NOTE**: Code for API is present in `<PROJECT_ROOT>/bio3dbeacons/api` directory.

##### Develop CLI locally

CLI is conveniently packed using Python [click](https://palletsprojects.com/p/click/) package which is an easy way of creating command line interfaces with less code. `<PROJECT_ROOT>/bio3dbeacons/cli/.py` is the entry point for the CLI application.

Follow below steps to start using the CLI,

CLI has an external dependency on [Gemmi program](https://gemmi.readthedocs.io/en/latest/install.html#gemmi-program) for converting PDB files to CIF. It is available as part of [conda-forge packages](https://anaconda.org/conda-forge/gemmi/files) or can be build from source by following below steps.

**NOTE**: Skip these steps if using conda to manage the environment as described in earlier section.

Make sure you have git, cmake, C++ compiler installed
For eg. on Ubuntu, `sudo apt install git cmake make g++`

```
$ git clone https://github.com/project-gemmi/gemmi.git
$ cd gemmi
$ cmake .
$ make
$ export GEMMI_BIN=$PWD/gemmi/gemmi
```

```
# Create a new Python (3.6+) virtual environment
$ python3 -m venv venv
```

If the environment is already created as part of API development, skip the previous step.

```
# activate the environment
$ source venv/bin/activate

# Install the dependencies
$ pip install -r bio3dbeacons/cli/requirements.txt

# Get the help menu of the CLI
$ python3 -m bio3dbeacons.cli --help
```

Use the help menu of various commands to see their usage.

For eg:

```
(venv) $ python3 -m bio3dbeacons.cli convert_pdb_to_cif --help
Usage: python -m bio3dbeacons.cli convert_pdb_to_cif [OPTIONS]

Options:
-i, --input-pdb TEXT Input PDB to convert, can be a directory in which
case all .pdb files will be converted [required]
-o, --output-cif TEXT Output CIF file, a directory in case a directory is
passed for --input-pdb [required]
--help Show this message and exit.
```

The CLI can also be distributed as a Python pip package, install and use it using below commands.

```
# activate the environment
$ source venv/bin/activate

# Update pip, wheel and setuptools
$ pip install --upgrade pip setuptools wheel

# Install the dependencies
$ pip install .

# Get the help menu of the CLI
$ bio3dbeacons_cli --help
```

To further make it more convenient for development and distribution, there is a docker image provided as well. Use below steps to build and run the CLI application.

```
# build the docker image and tag it
$ docker build -t bio3dbeacons .

# Get the help menu of the CLI
$ docker run -t bio3dbeacons bio3dbeacons_cli --help

# Run PDB to CIF conversion using the docker image
$ docker run -v $PWD/data:/data -t bio3dbeacons bio3dbeacons_cli convert_pdb_to_cif -i /data/pdb -o /data/cif
```

The above docker run command for PDB to CIF conversion assumes you have a `data/pdb` directory in current working directory with one or more PDB files. The command will convert the PDB files in `data/pdb` to `data/cif` directory.

### Unit Testing

Unit testing is performed with [pytest](https://pytest.org/).

pytest will automatically discover and run tests by recursively searching for folders and `.py` files prefixed with `test` for any functions prefixed by `test`.

Code coverage is provided by the [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) plugin.

Use the make command below to run the unit tests.

Please make sure to keep the docker compose services up as the tests will be running against Mongo DB docker instance since there are compatibility issues of using [mongomock](https://github.com/mongomock/mongomock) with [motor](https://motor.readthedocs.io/en/stable/tutorial-asyncio.html) asyncio framework.

```
# set the env variables from 'Develop API locally' section
$ make test
```

### Workflow automation using pre-commit hooks

Code formatting and PEP8 compliance are automated using [pre-commit](https://pre-commit.com/) hooks. This is configured in `.pre-commit-config.yaml` which will run these hooks before `commit` ting anything to the repository. Run below command to run all the pre-commit hooks.

```
$ make pre-commit
```
