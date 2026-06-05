.DEFAULT_GOAL := help

PY_DIR := python/src
TS_DIR := ts

.PHONY: help freeze py-deps run-web run-celery-worker run-celery-beat run-fe ts-deps

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nAvailable commands:\n\n"} /^[a-zA-Z_-]+:.*##/ {printf "  %-20s %s\n", $$1, $$2} END {print ""}' $(MAKEFILE_LIST)

freeze: ## Freeze dependencies into requirements.txt
	pip freeze > requirements.txt

# --------------
#  Install Deps
# --------------	

py-deps: ## Install all depedencies in requirements.txt
	pip install -r requirements.txt

ts-deps: ## Install frontend npm dependencies
	cd $(TS_DIR) && npm install

# --------------
#  Async Tasks
# --------------	

run-celery-worker: ## Start Celery worker
	cd $(PY_DIR) && celery -A celery_service.celery_run.celery worker --loglevel=info

run-celery-beat: ## Start Celery scheduler
	cd $(PY_DIR) && celery -A celery_service.celery_run.celery beat --loglevel=info


# --------------
#   Web Server
# --------------

run-web: ## Start Flask dev server
	flask --app $(PY_DIR)/run.py run --debug

run-web-prod: ## Start the production server
	cd python/src && waitress-serve --host 127.0.0.1 --port 8080 run:app

run-fe: ## Start frontend dev server
	cd $(TS_DIR) && npm run start

# --------------
#    Testing
# --------------

test-py: ## Run Python tests
	python -m pytest .

test-py-cov: ## Run Python tests with coverage
	python -m pytest ./python/src/tests --cov=python/src

test-fe: ## Run TS tests
	cd ./ts && npx vitest

test-fe-cov: ## Run TS tests with coverage
	cd ./ts && npx vitest --coverage