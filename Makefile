PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

render-start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

install:
	uv sync

build:
	./build.sh

dev:
	uv run flask --debug --app page_analyzer:app run

check:
	uv run ruff check .

test:
	uv run pytest

test-coverage:
	uv run pytest --cov=page_analyzer --cov-report xml

test-coverage-cons:
	uv run pytest --cov=page_analyzer

