SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

### Dependencies

PHONY: install-dev
install-dev: ## Install backend and frontend dependencies (dev)
	@$(MAKE) -C backend install-dev
	@$(MAKE) -C frontend install-dev

### Format and checks

PHONY: format
format:
	@$(MAKE) -C backend format
	@$(MAKE) -C frontend format

PHONY: clean
clean:
	@$(MAKE) -C backend clean
	@$(MAKE) -C frontend clean

### Help

.PHONY: help
help:
	@echo "Usage:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
