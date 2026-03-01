.PHONY: run install rebuild clean deploy

run:
	uv run python -m bot.main

install:
	uv sync

rebuild:
	rm -rf .venv
	uv sync

deploy:
	git pull
	uv sync
	pkill -f "python -m bot.main" || true
	nohup uv run python -m bot.main >> bot.log 2>&1 &
	@echo "Bot started. PID: $$!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -f autobook.db
