
Install

```
python3 -m venv venv
./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```


Start dependencies

```
docker-compose up -d
```


Start server

```
uvicorn bio3dbeacon.main:app --reload
```

Run tests

```
pytest
```