# minimalistic utility to test and develop locally

SHELL = /bin/sh
.DEFAULT_GOAL := help

.PHONY: build
build: ## bult image
	docker build -t test_image .

.PHONY: help
help: ## this colorful help
	@echo "Recipes for '$(notdir $(CURDIR))':"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""