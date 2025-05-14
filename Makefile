# Build and development commands

.PHONY: venv install install-dev test lint run clean

VENV_NAME?=venv
PYTHON=${VENV_NAME}/bin/python
PIP=${VENV_NAME}/bin/pip

# Create virtual environment
venv:
	python -m venv $(VENV_NAME)
	@echo "Virtual environment created. Activate with:"
	@echo "source $(VENV_NAME)/bin/activate  # Linux/Mac"
	@echo "$(VENV_NAME)\Scripts\activate    # Windows"

# Install production dependencies
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Production dependencies installed"

# Install development dependencies
install-dev: install
	$(PIP) install -r requirements-dev.txt
	@echo "Development dependencies installed"

# Run tests
test:
	$(PYTHON) -m pytest tests/ -v --cov=trade_simulator --cov-report=html

# Lint code
lint:
	$(PYTHON) -m flake8 trade_simulator
	$(PYTHON) -m mypy trade_simulator
	$(PYTHON) -m black --check trade_simulator
	$(PYTHON) -m isort --check-only trade_simulator

# Format code
format:
	$(PYTHON) -m black trade_simulator
	$(PYTHON) -m isort trade_simulator

# Run application
run:
	$(PYTHON) -m trade_simulator.main

# Clean up
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	@echo "Cleaned Python artifacts"