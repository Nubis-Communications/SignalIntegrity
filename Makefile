
install: 
	pip install -r requirements.txt --upgrade
	pip install -r requirements_dev.txt --upgrade
	pip install -e .
	pre-commit install

test:
	coverage run --source='SignalIntegrity' Test/TestSignalIntegrity/TestAll.py > /dev/null

cov:
	pytest --cov=SignalIntegrity

mypy:
	mypy . --ignore-missing-imports

flake8:
	flake8 --select RST

pylint:
	pylint SignalIntegrity

pydocstyle:
	pydocstyle SignalIntegrity

doc8:
	doc8 docs/

update:
	pur

update-pre:
	pre-commit autoupdate --bleeding-edge
