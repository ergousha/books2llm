.PHONY: install run clean lint venv

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt
	# Marker might need additional setup for models
	# $(PYTHON) -c "import marker; marker.download_models()" # Example if needed

run:
	$(PYTHON) -m src.pipeline

clean:
	rm -rf input/*
	rm -rf output/*
	# rm -rf $(VENV)

lint:
	$(PYTHON) -m flake8 src/
