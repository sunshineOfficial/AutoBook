# systemd Service Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the `nohup`/PID-file deployment with a systemd service so journald manages log rotation automatically.

**Architecture:** A `autobook.service` unit file lives in the repo root and gets copied to `/etc/systemd/system/` by a new `make install-service` target. Routine deploys use `make deploy` which calls `systemctl restart`. The `.env` file is loaded by systemd via `EnvironmentFile=` — python-dotenv remains but becomes a no-op at runtime.

**Tech Stack:** systemd, journald, GNU Make, uv, Python 3 (venv at `.venv/`)

---

### Task 1: Create the service unit file in the repo

**Files:**
- Create: `autobook.service`

> No tests for infrastructure files. Verification is done by running the service in Task 3.

**Step 1: Create `autobook.service` in the repo root**

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

**Step 2: Commit**

```bash
git add autobook.service
git commit -m "feat: add systemd service unit file"
```

---

### Task 2: Update the Makefile

**Files:**
- Modify: `Makefile`

> No tests. Verification is `make deploy` succeeding in Task 3.

**Step 1: Replace the Makefile with the updated version**

New content (full file replacement):

```makefile
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
	systemctl enable autobook
	systemctl start autobook
	@echo "Service installed and started."

deploy:
	git pull
	uv sync
	systemctl daemon-reload
	systemctl restart autobook

logs:
	journalctl -u autobook -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -f autobook.db
```

**Step 2: Commit**

```bash
git add Makefile
git commit -m "feat: replace nohup deploy with systemctl; add install-service and logs targets"
```

---

### Task 3: First-time setup on the server (manual steps — not automated)

> These steps run **on the server** after deploying the new code. They are one-time only.

**Step 1: Stop the old nohup process if still running**

```bash
cd /root/AutoBook
if [ -f bot.pid ]; then kill $(cat bot.pid) 2>/dev/null || true; rm -f bot.pid; fi
```

**Step 2: Pull the new code and sync dependencies**

```bash
git pull
uv sync
```

**Step 3: Install and start the service**

```bash
make install-service
```

Expected output:
```
Created symlink /etc/systemd/system/multi-user.target.wants/autobook.service → /etc/systemd/system/autobook.service.
Service installed and started.
```

**Step 4: Verify the service is running**

```bash
systemctl status autobook
```

Expected: `Active: active (running)`

**Step 5: Verify logs are flowing into journald**

```bash
journalctl -u autobook -n 20
```

Expected: aiogram startup lines visible.

**Step 6: Set journal log cap (optional but recommended)**

Edit `/etc/systemd/journald.conf` — find or add under `[Journal]`:
```
SystemMaxUse=50M
```

Then:
```bash
systemctl restart systemd-journald
```

---

### Task 4: Clean up old log artefacts (on server, after confirming service is healthy)

**Step 1: Remove the old log file**

```bash
rm -f /root/AutoBook/bot.log
```

**Step 2: Confirm disk space freed**

```bash
df -h /
```
