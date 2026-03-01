# Admin Notifications Design

**Date:** 2026-03-01
**Feature:** Notify admin on booking and cancellation events

## Summary

When a user books or cancels a seat, the bot sends a direct message to the admin (`ADMIN_ID`) with basic info: the user's name/username and the seat number (for bookings) or just the user name (for cancellations).

## Scope

Changes limited to `bot/handlers/user.py` only.

## Notification Format

- **Booking:** `✅ @username забронировал место {seat_number}`
- **Cancellation:** `❌ @username отменил бронирование`

If the user has no username, fall back to `User {user_id}`.

## Implementation

1. Import `ADMIN_ID` from `bot.config` in `user.py`
2. In `on_book` — after successful booking confirmation, send notification via `callback.bot.send_message(ADMIN_ID, ...)`
3. In `on_cancel` — after confirmed cancellation (`removed == True`), send notification via `callback.bot.send_message(ADMIN_ID, ...)`

## Decisions

- **Approach A chosen** (inline in handlers) over a dedicated `notify.py` helper — simpler for a small feature
- Seat number is included for bookings (returned by `db.book_seat`), omitted for cancellations (not tracked on delete)
- No changes to DB, config, keyboards, admin handler, or main
