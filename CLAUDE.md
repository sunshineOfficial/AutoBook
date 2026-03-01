# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the bot
uv run python -m bot.main
```

## Architecture

AutoBook is a Telegram bot for car seat reservation built with **aiogram 3.x** (async) and **aiosqlite** (SQLite).

### Entry point

`bot/main.py` initializes the database, creates the `Bot` and `Dispatcher`, registers routers, and starts long-polling.

### Module overview

| File | Role |
|------|------|
| `bot/config.py` | Loads `BOT_TOKEN` and `ADMIN_ID` from `.env`; exits on missing values |
| `bot/db.py` | All database logic; `TOTAL_SEATS = 4` controls capacity; SQLite at `autobook.db` |
| `bot/keyboards.py` | `CallbackData` classes (`BookCallback`, `CancelCallback`, `RefreshCallback`) and `seats_keyboard()` builder |
| `bot/handlers/user.py` | User router — `/start`, `/seats`, and inline button callbacks |
| `bot/handlers/admin.py` | Admin router (filtered to `ADMIN_ID`) — `/reset`, `/kick <user_id\|@username>`, `/toggle` |

### Data model

Two SQLite tables:
- `settings(key, value)` — currently only stores `car_available` flag (`"1"` / `"0"`)
- `bookings(seat_number PK, user_id, username, booked_at)` — one row per occupied seat; each user can hold at most one booking

### Request flow

1. User sends `/seats` → `user.cmd_seats` → `_send_seats()` checks availability, fetches seats, renders inline keyboard
2. Inline buttons trigger callbacks (`BookCallback`, `CancelCallback`, `RefreshCallback`) which mutate the DB then call `_send_seats(..., edit=True)` to update the message in-place
3. Admin commands bypass normal user flow via a router-level filter (`F.from_user.id == ADMIN_ID`)

## Configuration

Copy `.env.example` to `.env` and set:
- `BOT_TOKEN` — Telegram bot token from @BotFather
- `ADMIN_ID` — your Telegram numeric user ID
