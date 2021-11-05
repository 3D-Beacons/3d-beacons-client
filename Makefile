default: test

test:
	pip install -r requirements.dev.txt
	pip install .
	coverage run  --source bio3dbeacons -m pytest --junitxml=report.xml tests
	coverage xml -o coverage/cobertura-coverage.xml
	coverage report -m

pre-commit:
	pip install pre-commit
	pre-commit install && pre-commit run --all
