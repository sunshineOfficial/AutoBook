# systemd Service for AutoBook

**Date:** 2026-03-01
**Status:** Approved

## Problem

The current `make deploy` uses `nohup ... >> bot.log 2>&1` with a PID file. `bot.log` grows unbounded and has caused low disk space on the server.

## Solution

Replace the `nohup` deployment with a systemd service. journald captures all output and handles log rotation automatically.

## Approach

System service (`/etc/systemd/system/`) with `EnvironmentFile=` pointing at the existing `.env` file. systemd injects `BOT_TOKEN` and `ADMIN_ID` directly into the process environment — no changes to bot code required.

## Service Unit

File: `/etc/systemd/system/autobook.service`

```ini
[Unit]
Description=AutoBook Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/AutoBook
EnvironmentFile=/root/AutoBook/.env
ExecStart=/root/AutoBook/.venv/bin/python -m bot.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`ExecStart` calls the venv Python directly (not `uv run`) for reliability in a non-interactive service context.

## Makefile Changes

Replace `nohup`/PID logic in `deploy` with `systemctl restart`. Add `logs` target for convenience.

```makefile
deploy:
	git pull
	uv sync
	systemctl daemon-reload
	systemctl restart autobook

logs:
	journalctl -u autobook -f
```

## Journal Log Retention

Set an explicit cap in `/etc/systemd/journald.conf`:

```
SystemMaxUse=50M
```

Then restart journald: `systemctl restart systemd-journald`.

## What Does Not Change

- `.env` file location and format
- python-dotenv remains in code (harmless no-op when vars already in environment)
- `make run` for local development
