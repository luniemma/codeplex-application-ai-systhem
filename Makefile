# Makefile for Codeplex AI

.PHONY: help install dev prod test lint format clean docker-build docker-up docker-down docker-logs k8s-up k8s-down k8s-status k8s-urls k8s-nuke

help:
	@echo "Codeplex AI - Available Commands"
	@echo "================================"
	@echo "make install        - Install dependencies"
	@echo "make dev            - Run development server"
	@echo "make prod           - Run production server"
	@echo "make test           - Run tests"
	@echo "make test-cov       - Run tests with coverage"
	@echo "make lint           - Run linting"
	@echo "make format         - Format code"
	@echo "make clean          - Clean up generated files"
	@echo "make docker-build   - Build Docker image"
	@echo "make docker-up      - Start Docker containers (prod)"
	@echo "make docker-dev     - Start Docker containers (dev)"
	@echo "make docker-down    - Stop Docker containers"
	@echo "make docker-logs    - View Docker logs"
	@echo ""
	@echo "Kubernetes (uses whatever cluster kubectl currently points at):"
	@echo "make k8s-up         - Apply manifests + wait + start port-forwards (18000/19090/13000)"
	@echo "make k8s-down       - Stop port-forwards (manifests stay applied)"
	@echo "make k8s-status     - Show pod + port-forward state"
	@echo "make k8s-urls       - Print the browse-able endpoint URLs"
	@echo "make k8s-nuke       - Delete the namespace (everything goes)"

install:
	pip install -r requirements.txt

dev:
	FLASK_ENV=development FLASK_APP=main.py flask run --reload

prod:
	gunicorn -c gunicorn_config.py main:app

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	flake8 app/ main.py --max-line-length=100
	pylint app/ main.py

format:
	black app/ main.py tests/
	isort app/ main.py tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

docker-build:
	docker build -t codeplex-ai:latest .
	docker build -t codeplex-ai:dev -f Dockerfile.dev .

docker-up:
	docker-compose up -d

docker-dev:
	docker-compose -f docker-compose.dev.yml up

docker-down:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

docker-logs:
	docker-compose logs -f codeplex-api

docker-logs-dev:
	docker-compose -f docker-compose.dev.yml logs -f codeplex-api-dev

k8s-up:
	bash scripts/dev-cluster.sh up

k8s-down:
	bash scripts/dev-cluster.sh down

k8s-status:
	bash scripts/dev-cluster.sh status

k8s-urls:
	bash scripts/dev-cluster.sh urls

k8s-nuke:
	bash scripts/dev-cluster.sh nuke

db-migrate:
	alembic upgrade head

db-makemigrations:
	alembic revision --autogenerate -m "Auto migration"

requirements-update:
	pip list --outdated

requirements-freeze:
	pip freeze > requirements-lock.txt

venv-create:
	python -m venv venv

venv-activate:
	@echo "Run: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"

setup: venv-create install
	@echo "Setup complete! Run 'make venv-activate' to activate the virtual environment"

