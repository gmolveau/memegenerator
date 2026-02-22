SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

### Dependencies

.PHONY: install-dev
install-dev: ## Install development dependencies
	npm ci

.PHONY: upgrade
upgrade: ## Upgrade all dependencies
	npm update --loglevel verbose

### Application

.PHONY: run-dev
run-dev: ## Run dev mode
	pnpm run dev --open

### Tests

.PHONY: tests
tests: ## Run frontend tests
	npm run tests

### Format and checks

.PHONY: lint-check
lint-check: ## Check lint code.
	npm run type-check
	npm run lint-check

.PHONY: lint-fix
lint-fix: ## Lint code and fix.
	npm run type-check
	npm run lint-fix

.PHONY: lint
lint: lint-fix ## Lint code and fix.

.PHONY: format-fix
format-fix: ## Fix format.
	npm run format-fix

.PHONY: format
format: format-fix ## Fix format.

.PHONY: format-check
format-check: ## Format code check.
	npm run format-check

.PHONY: audit-check
audit-check: ## Audit dependencies.
	npm audit

.PHONY: checks
checks: ## Run checks on code (lint, format, api types)
	$(MAKE) lint-check
	$(MAKE) format-check
	$(MAKE) openapi-check
	# $(MAKE) audit-check

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
