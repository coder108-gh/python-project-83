PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

install:
	uv sync

build:
	./build.sh

dev:
	uv run flask --debug --app page_analyzer:app run

check:
	uv run ruff check .
