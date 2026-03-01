.PHONY: run install rebuild clean deploy logs install-service

run:
	uv run python -m bot.main

install:
	uv sync

rebuild:
	rm -rf .venv
	uv sync

install-service:
	cp autobook.service /etc/systemd/system/autobook.service
	systemctl daemon-reload
	systemctl enable --now autobook
	@echo "Service installed and started."

deploy:
	git pull
	uv sync
	cp autobook.service /etc/systemd/system/autobook.service
	systemctl daemon-reload
	systemctl restart autobook

logs:
	journalctl -u autobook -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -f autobook.db
