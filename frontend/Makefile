SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

### Dependencies

.PHONY: install-dev
install-dev: ## Install development dependencies
	pnpm install

.PHONY: upgrade
upgrade: ## Upgrade all dependencies
	pnpm update --loglevel verbose

### Application

.PHONY: run-dev
run-dev: ## Run dev mode
	pnpm run dev --open

### Tests

.PHONY: tests
tests: ## Run frontend tests
	pnpm run tests

### Format and checks

.PHONY: lint
lint: ## Lint code and fix.
	pnpm run lint

.PHONY: format
format: ## Fix format.
	pnpm run format

.PHONY: checks
checks: ## Run checks on code
	$(MAKE) lint

### Misc

.PHONY: clean
clean: ## Clean folder
	rm -rf node_modules
	rm -rf test-reports
	rm -rf dist

### Help

.PHONY: help
help:
	@echo "Usage:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
