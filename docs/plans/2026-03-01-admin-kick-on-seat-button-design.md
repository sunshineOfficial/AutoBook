# Admin Kick on Seat Button — Design

**Date:** 2026-03-01
**Status:** Approved

## Summary

When the admin opens the seat list and presses a booked seat button, a two-step inline confirmation keyboard replaces the seat list. The admin can confirm the kick or cancel and return to the seat list.

## Keyboard Changes (`bot/keyboards.py`)

- `seats_keyboard(seats, user_id, is_admin=False)` — new `is_admin` parameter
  - Free seats → `RefreshCallback` (unchanged)
  - Booked seats (admin view) → `AdminSeatCallback(seat_number=N)`
  - Booked seats (user view) → `RefreshCallback` (unchanged)
- New `AdminSeatCallback(CallbackData, prefix="admin_seat")` — carries `seat_number: int`
- New `KickConfirmCallback(CallbackData, prefix="kick_confirm")` — carries `seat_number: int`
- New `kick_confirm_keyboard(seat_number, username)` builder — returns two buttons:
  - "✅ Kick @username from seat N" → `KickConfirmCallback(seat_number=N)`
  - "❌ Cancel" → `RefreshCallback()`

## Handler Flow (`bot/handlers/admin.py`)

Two new callback handlers, filtered to `ADMIN_ID`:

1. **`on_admin_seat(AdminSeatCallback)`**
   - Look up current occupant of `seat_number` from the DB
   - Edit the message keyboard to the confirmation keyboard
   - `callback.answer()` silently

2. **`on_kick_confirm(KickConfirmCallback)`**
   - Call `db.kick_user_by_seat(seat_number)` → returns evicted `user_id` or `None`
   - `callback.answer("✅ Kicked", show_alert=True)`
   - Re-render seat list via `_send_seats(callback.message, user_id=ADMIN_ID, edit=True)`

## `_send_seats` Change (`bot/handlers/user.py`)

`_send_seats(message, user_id, edit=False)` detects if `user_id == ADMIN_ID` and passes `is_admin=True` to `seats_keyboard()`.

## Database (`bot/db.py`)

New function: `kick_user_by_seat(seat_number: int) -> int | None`
- Deletes the booking for `seat_number`
- Returns the evicted `user_id`, or `None` if seat was already free

## Files Changed

| File | Change |
|------|--------|
| `bot/keyboards.py` | Add `AdminSeatCallback`, `KickConfirmCallback`, `kick_confirm_keyboard()`; update `seats_keyboard()` |
| `bot/db.py` | Add `kick_user_by_seat()` |
| `bot/handlers/user.py` | Pass `is_admin` flag to `seats_keyboard()` |
| `bot/handlers/admin.py` | Add `on_admin_seat` and `on_kick_confirm` handlers |
