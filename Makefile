.PHONY: test
test:
	@cd tests; PYTHONPATH=.. py.test --tb=short
