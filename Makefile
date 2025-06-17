.PHONY: help install test run clean docker-build docker-run setup validate

# Default target
.DEFAULT_GOAL := help

# Python interpreter
PYTHON := python3
PIP := pip3

# Colors
COLOR_RESET = \033[0m
COLOR_BOLD = \033[1m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m

help: ## Show this help message
	@echo '$(COLOR_BOLD)ULTRATHINK Makefile$(COLOR_RESET)'
	@echo ''
	@echo 'Usage:'
	@echo '  $(COLOR_GREEN)make$(COLOR_RESET) $(COLOR_YELLOW)<target>$(COLOR_RESET)'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(COLOR_GREEN)%-15s$(COLOR_RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	$(PIP) install -r requirements.txt
	$(PYTHON) -m playwright install chromium
	@echo "$(COLOR_GREEN)✓ Dependencies installed$(COLOR_RESET)"

setup: ## Initial setup
	$(PYTHON) scripts/setup.py
	@echo "$(COLOR_GREEN)✓ Setup complete$(COLOR_RESET)"

validate: ## Validate configuration
	$(PYTHON) manage.py validate

test: ## Run tests
	pytest -v

test-coverage: ## Run tests with coverage
	pytest --cov=. --cov-report=html --cov-report=term

run: ## Run once
	$(PYTHON) run.py --once

run-test: ## Run with test data
	$(PYTHON) run.py --test --once

run-preview: ## Run in preview mode
	$(PYTHON) run.py --preview --once

clean: ## Clean generated files
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	$(PYTHON) manage.py clean
	@echo "$(COLOR_GREEN)✓ Cleaned$(COLOR_RESET)"

docker-build: ## Build Docker image
	docker-compose build
	@echo "$(COLOR_GREEN)✓ Docker image built$(COLOR_RESET)"

docker-run: ## Run with Docker
	docker-compose up

docker-run-daemon: ## Run Docker in background
	docker-compose up -d

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-stop: ## Stop Docker containers
	docker-compose down

backup: ## Create backup
	$(PYTHON) scripts/backup.py

export: ## Export data
	$(PYTHON) scripts/export.py

format: ## Format code
	black .
	@echo "$(COLOR_GREEN)✓ Code formatted$(COLOR_RESET)"

lint: ## Run linters
	flake8 .
	mypy .
	@echo "$(COLOR_GREEN)✓ Linting complete$(COLOR_RESET)"

stats: ## Show statistics
	$(PYTHON) manage.py stats

add-user: ## Add a new user (usage: make add-user EMAIL=user@example.com)
	@if [ -z "$(EMAIL)" ]; then \
		echo "Error: EMAIL is required. Usage: make add-user EMAIL=user@example.com"; \
		exit 1; \
	fi
	$(PYTHON) manage.py add_user $(EMAIL)