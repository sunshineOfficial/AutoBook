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
	@if [ -f bot.pid ]; then kill $$(cat bot.pid) 2>/dev/null || true; rm -f bot.pid; fi
	nohup uv run python -m bot.main >> bot.log 2>&1 & echo $$! > bot.pid
	@echo "Bot started. PID: $$(cat bot.pid)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -f autobook.db
