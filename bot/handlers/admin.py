from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot import db
from bot.config import ADMIN_ID

router = Router()
router.message.filter(F.from_user.id == ADMIN_ID)


@router.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    await db.clear_all_bookings()
    await message.answer("\u2705 All bookings have been cleared.")


@router.message(Command("kick"))
async def cmd_kick(message: Message) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Usage: /kick <user_id or @username>")
        return

    target = args[1].strip()

    # Try to parse as user_id
    if target.isdigit():
        user_id = int(target)
        removed = await db.kick_user(user_id)
        if removed:
            await message.answer(f"\u2705 Removed booking for user {user_id}.")
        else:
            await message.answer(f"No booking found for user {user_id}.")
        return

    # Try to match by username
    username = target.lstrip("@")
    seats = await db.get_all_seats()
    for seat in seats:
        if seat["username"] and seat["username"].lower() == username.lower():
            await db.kick_user(seat["user_id"])
            await message.answer(f"\u2705 Removed booking for @{username}.")
            return

    await message.answer(f"No booking found for {target}.")


@router.message(Command("toggle"))
async def cmd_toggle(message: Message) -> None:
    new_state = await db.toggle_car_available()
    status = "available \U0001f7e2" if new_state else "unavailable \U0001f534"
    await message.answer(f"Car is now {status}.")
