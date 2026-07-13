.PHONY: help setup load validate test report clean

help:
	@echo "N100 Financial Intelligence Platform - Sprint 1"
	@echo "Available targets:"
	@echo "  make setup    - Install dependencies"
	@echo "  make load     - Load all data files"
	@echo "  make validate - Run data quality checks"
	@echo "  make test     - Run unit tests"
	@echo "  make report   - Generate audit reports"
	@echo "  make clean    - Clean output files"

setup:
	pip install -r requirements.txt

load:
	python src/etl/loader.py

validate:
	python src/etl/validator.py

test:
	pytest tests/ -v --cov=src

report:
	@echo "Reports generated in output/"

clean:
	rm -f db/nifty100.db
	rm -f output/*.csv
