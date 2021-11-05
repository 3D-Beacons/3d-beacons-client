# 3D-Beacons Client
This is an implementation of 3D-Beacons client which provides various tools and infrastructure for hosting local models and contribute to the [3D-Beacons](https://github.com/3D-Beacons/3D-Beacons/wiki) network.

More about 3D-Beacons can be found in the [WikiPages](https://github.com/3D-Beacons/3D-Beacons/wiki)


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


## Getting started


### Local development
For local development, please follow the below instructions.

##### Set the environment variables

<pre>
<b>MONGO_USERNAME</b>: username for Mongo DB
<b>MONGO_PASSWORD</b>: password for Mongo DB
<b>PROVIDER</b>: Provider name. For eg: PDBE
<b>MONGO_DB_HOST</b>: Mongo DB host. Used by API, set it to <b>mongodb:27017</b> if using the docker compose service.
<b>MODEL_FORMAT</b>: Format of the model. For eg: MMCIF
<b>ASSETS_URL</b>: Static assets URL, location where the hosted model files can be accessed.
Set to <b>localhost/static</b> if using docker compose service. This is used by API to return <i>modelUrl</i> where the model file can be accessed.
</pre>
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

<pre>
<code>
# Create a new Python (3.6+) virtual environment
$ python3 -m venv venv

# activate the environment
$ source venv/bin/activate

# Install the dependencies
$ pip install -r bio3dbeacons/api/requirements.txt
</code>
</pre>

The above commands will create a new Python virtual environment and install the dependencies required to run the API. To use environment variables, API is using a python package `python-dotenv` which is a convenient way of keeping the variables in a `.env` file in the project directory.
So, create a file named `.env` in project root directory and set below environment variables.

<pre>
<b>MONGO_USERNAME</b>: Same as set in earlier section
<b>MONGO_PASSWORD</b>: Same as set in earlier section
<b>PROVIDER</b>: Same as set in earlier section
<b>MONGO_DB_HOST</b>: localhost:27017 (This is where Mongo DB docker compose service is accessible)
<b>MODEL_FORMAT</b>: Same as set in earlier section
<b>ASSETS_URL</b>: localhost/static (This is where NGINX docker compose service is accessible)
</pre>

Now that dependencies and environment variables are available, run the API locally using [uvicorn](https://www.uvicorn.org/) which is a lightning fast ASGI server implementation. This is already installed using the `pip` command executed before.

```
uvicorn bio3dbeacons.api.main:app --reload
```

Now access the local API docs using [http://localhost:8000/docs](http://localhost:8000/docs). The server will keep monitoring the files and reloads the instance without the need for restarting the server after making any code changes.

**NOTE**: Code for API is present in `<PROJECT_ROOT>/bio3dbeacons/api` directory.


##### Develop CLI locally
CLI is conveniently packed using Python [click](https://palletsprojects.com/p/click/) package which is an easy way of creating command line interfaces with less code. `<PROJECT_ROOT>/bio3dbeacons/cli/.py` is the entry point for the CLI application.

Follow below steps to start using the CLI,

CLI has an external dependency on [Gemmi program](https://gemmi.readthedocs.io/en/latest/install.html#gemmi-program) for converting PDB files to CIF. It is available as part of [conda-forge packages](https://anaconda.org/conda-forge/gemmi/files) or can be build from source by following below steps

<pre>
Make sure you have git, cmake, C++ compiler installed
For eg. on Ubuntu, <b>sudo apt install git cmake make g++</b>
</pre>

```
$ git clone https://github.com/project-gemmi/gemmi.git
$ cd gemmi
$ cmake .
$ make
$ export PATH=$PATH:$PWD/gemmi
```


<pre>
<code>
# Create a new Python (3.6+) virtual environment
$ python3 -m venv venv
</code>
</pre>

If the environment is already created as part of API development, skip the previous step.

<pre>
<code>

# activate the environment
$ source venv/bin/activate

# Install the dependencies
$ pip install -r bio3dbeacons/cli/requirements.txt

# Get the help menu of the CLI
$ python3 -m bio3dbeacons.cli --help
</code>
</pre>

Use the help menu of various commands to see their usage.

For eg:
```
(venv) $ python3 -m bio3dbeacons.cli convert_pdb_to_cif --help
Usage: python -m bio3dbeacons.cli convert_pdb_to_cif [OPTIONS]

Options:
  -i, --input-pdb TEXT   Input PDB to convert, can be a directory in which
                         case all .pdb files will be converted  [required]
  -o, --output-cif TEXT  Output CIF file, a directory in case a directory is
                         passed for --input-pdb  [required]
  --help                 Show this message and exit.

```

The CLI can also be distributed as a Python pip package, install and use it using below commands.

<pre>
<code>

# activate the environment
$ source venv/bin/activate

# Update pip, wheel and setuptools
$ pip install --upgrade pip setuptools wheel

# Install the dependencies
$ pip install .

# Get the help menu of the CLI
$ bio3dbeacons_cli --help
</code>
</pre>

To further make it more convenient for development and distribution, there is a docker image provided as well. Use below steps to build and run the CLI application.

<pre>
<code>

# build the docker image and tag it
$ docker build -t bio3dbeacons .

# Get the help menu of the CLI
$ docker run -t bio3dbeacons bio3dbeacons_cli --help

# Run PDB to CIF conversion using the docker image
$ docker run -v $PWD/data:/data -t bio3dbeacons bio3dbeacons_cli convert_pdb_to_cif -i /data/pdb -o /data/cif
</code>
</pre>

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

### Workflow automation using pre-commit hooks ###

Code formatting and PEP8 compliance are automated using [pre-commit](https://pre-commit.com/) hooks. This is configured in `.pre-commit-config.yaml` which will run these hooks before `commit` ting anything to the repository. Run below command to run all the pre-commit hooks.

```
$ make pre-commit
```
