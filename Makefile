#
#  Makefile
#


include default.mk

SRC = owid tests

# watch:
# 	poetry run watchmedo shell-command -c 'clear; make unittest' --recursive --drop .

check-typing: .venv
	@echo '==> Checking types'
	poetry run mypy --strict -p owid -p tests

coverage: .venv
	@echo '==> Unit testing with coverage'
	poetry run pytest --cov=owid --cov-report=term-missing --cov-report=html:.report-coverage tests

linting: .venv
	@echo '==> Linting'
	@poetry run flake8 --format=html --htmldir=.report-linting owid

watch: .venv
	@echo '==> Watching for changes and re-running tests'
	poetry run watchmedo shell-command -c 'clear; make check-formatting lint check-typing coverage' --recursive --drop .

bump: .venv
	@echo '==> Bumping version'
	poetry run bump2version $(part)
