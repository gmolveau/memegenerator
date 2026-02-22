SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

### Dependencies

.PHONY: install
install: ## install prod dependencies
	uv sync --locked

.PHONY: install-dev
install-dev: ## install prod+dev dependencies
	uv sync --locked --dev

.PHONY: upgrade
upgrade: ## upgrade all dependencies
	uv sync --upgrade

### Application



### Database

.PHONY: new-migrate
new-migrate: ## Auto-generate a new migration.
	DOTENV=.env.dev uv run alembic -c migrations/alembic.ini revision --autogenerate -m $(NAME)

.PHONY: migrate
migrate: ## Run the migrations (will update the database).
	uv run alembic -c migrations/alembic.ini upgrade head

### Format and checks

.PHONY: ruff
ruff: ## Format code with ruff
	uv run ruff check . --fix
	uv run ruff format .

.PHONY: ruff-check
ruff-check:	## Check that the code is linted using ruff
	uv run ruff check src tests cli migrations
	uv run ruff format --check src src tests cli migrations

.PHONY: ty
ty: ## Run ty static type check
	uv run ty check src tests cli migrations

.PHONY: bandit
bandit:	## Run a static security analysis of the code using bandit
	uv run bandit -c pyproject.toml -r src

.PHONY: alembic-check
alembic-check: ## Run the alembic check
	uv run alembic -c migrations/alembic.ini check

.PHONY: checks
checks:
	@$(MAKE) ty ruff-check bandit

PHONY: format
format:
	@$(MAKE) ruff

### Misc

.PHONY: clean
clean:
	rm -rf .venv
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.ty_cache ' -delete
	find . -type d -name '.pytest_cache ' -delete
	find . -type d -name '.ruff_cache' -delete
	rm -f coverage coverage.xml
	rm -rf .report

### Help

.PHONY: help
help: ## help message
	@echo "Usage:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
