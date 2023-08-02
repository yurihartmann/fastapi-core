
default:
	@echo "=== Utils FastApi Core === \n"
	@echo "    make lint  = Run linters"
	@echo "    make test  = Run tests and generate coverage"

lint:
	@./scripts/lint.sh

test:
	@pytest
