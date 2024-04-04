SHELL = /bin/sh
.DEFAULT_GOAL := help

.PHONY: .build
.build: ## packages docker image
	docker build -t test-image:latest .

.PHONY: run-failing
run-failing: .build ## produces failing results
	docker run -it --rm --privileged test-image:latest ./code_fails.sh

.PHONY: run-working
run-working: .build  ## produces working results
	docker run -it --rm  --privileged test-image:latest ./code_works.sh

.PHONY: help
help: ## this colorful help
	@echo "Recipes for '$(notdir $(CURDIR))':"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""