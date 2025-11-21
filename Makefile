.PHONY: install run clean lint venv

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt
	# Marker might need additional setup for models
	# $(PYTHON) -c "import marker; marker.download_models()" # Example if needed

run:
	$(PYTHON) -m src.pipeline

clean:
	rm -rf output/*
	rm -rf $(VENV)

lint:
	$(PYTHON) -m flake8 src/
