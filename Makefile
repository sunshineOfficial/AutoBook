.PHONY: run install rebuild clean

run:
	uv run python -m bot.main

install:
	uv sync

rebuild:
	rm -rf .venv
	uv sync

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -f autobook.db
