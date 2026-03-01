# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Install with dev dependencies (pytest)
uv sync --group dev

# Run the bot
uv run python -m bot.main

# Run tests
uv run pytest -v
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
| `bot/keyboards.py` | `CallbackData` classes (`BookCallback`, `CancelCallback`, `RefreshCallback`, `AdminSeatCallback`, `KickConfirmCallback`) and keyboard builders (`seats_keyboard()`, `kick_confirm_keyboard()`) |
| `bot/handlers/user.py` | User router — `/start`, `/seats`, and inline button callbacks |
| `bot/handlers/admin.py` | Admin router (filtered to `ADMIN_ID`) — `/reset`, `/kick <user_id\|@username>`, `/toggle`; inline kick via `AdminSeatCallback` / `KickConfirmCallback` |
| `tests/test_db.py` | Tests for `kick_user_by_seat` |
| `tests/test_keyboards.py` | Tests for admin keyboard callbacks and `seats_keyboard` |

### Data model

Two SQLite tables:
- `settings(key, value)` — currently only stores `car_available` flag (`"1"` / `"0"`)
- `bookings(seat_number PK, user_id, username, booked_at)` — one row per occupied seat; each user can hold at most one booking

### Request flow

1. User sends `/seats` → `user.cmd_seats` → `_send_seats()` checks availability, fetches seats, renders inline keyboard
2. Inline buttons trigger callbacks (`BookCallback`, `CancelCallback`, `RefreshCallback`) which mutate the DB then call `_send_seats(..., edit=True)` to update the message in-place
3. Admin commands and callbacks bypass normal user flow via router-level filters (`F.from_user.id == ADMIN_ID` on both `.message` and `.callback_query`)

### Admin inline kick flow

When the admin calls `/seats`, `_send_seats` detects `user_id == ADMIN_ID` and passes `is_admin=True` to `seats_keyboard()`. Booked seat buttons get `AdminSeatCallback(seat_number=N)` instead of `RefreshCallback`.

1. Admin presses a booked seat → `on_admin_seat` re-fetches DB state; if still occupied, replaces the keyboard with `kick_confirm_keyboard()` (confirm + cancel buttons)
2. Admin confirms → `on_kick_confirm` calls `db.kick_user_by_seat(seat_number)`, shows an alert, re-renders the seat list
3. Admin cancels → `RefreshCallback` fires, seat list refreshes unchanged

## Localisation

All user-facing strings are in Russian. Do not introduce English text in bot messages, button labels, or alerts.

## Configuration

Copy `.env.example` to `.env` and set:
- `BOT_TOKEN` — Telegram bot token from @BotFather
- `ADMIN_ID` — your Telegram numeric user ID
