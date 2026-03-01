from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from bot import db
from bot.keyboards import (
    BookCallback,
    CancelCallback,
    RefreshCallback,
    seats_keyboard,
)

router = Router()


async def _send_seats(message: Message, user_id: int, edit: bool = False) -> None:
    available = await db.is_car_available()
    if not available:
        text = "\U0001f6ab Car is not available right now."
        if edit:
            await message.edit_text(text, reply_markup=None)
        else:
            await message.answer(text)
        return

    seats = await db.get_all_seats()
    free = sum(1 for s in seats if s["user_id"] is None)

    seat_icons = {1: "1\ufe0f\u20e3", 2: "2\ufe0f\u20e3", 3: "3\ufe0f\u20e3", 4: "4\ufe0f\u20e3"}
    lines = [f"\U0001f697 Car Seats ({free} available):\n"]
    for seat in seats:
        num = seat["number"]
        icon = seat_icons.get(num, str(num))
        if seat["user_id"] is None:
            lines.append(f"{icon} Seat {num}: Free")
        else:
            name = f"@{seat['username']}" if seat["username"] else f"User {seat['user_id']}"
            lines.append(f"{icon} Seat {num}: {name}")

    text = "\n".join(lines)
    kb = seats_keyboard(seats, user_id)

    if edit:
        try:
            await message.edit_text(text, reply_markup=kb.as_markup())
        except TelegramBadRequest:
            pass  # Content unchanged, nothing to update
    else:
        await message.answer(text, reply_markup=kb.as_markup())


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "\U0001f44b Welcome to AutoBook!\n\n"
        "I help you check and reserve car seats.\n\n"
        "Use /seats to see available seats and book one."
    )


@router.message(Command("seats"))
async def cmd_seats(message: Message) -> None:
    await _send_seats(message, user_id=message.from_user.id)


@router.callback_query(BookCallback.filter())
async def on_book(callback: CallbackQuery) -> None:
    available = await db.is_car_available()
    if not available:
        await callback.answer("\U0001f6ab Car is not available right now.", show_alert=True)
        return

    user_id = callback.from_user.id
    username = callback.from_user.username
    seat = await db.book_seat(user_id, username)

    if seat is None:
        seats = await db.get_all_seats()
        user_booked = any(s["user_id"] == user_id for s in seats)
        if user_booked:
            await callback.answer("You already have a booking!", show_alert=True)
        else:
            await callback.answer("No free seats available.", show_alert=True)
        return

    await callback.answer(f"Booked seat {seat}!", show_alert=True)
    await _send_seats(callback.message, user_id=user_id, edit=True)


@router.callback_query(CancelCallback.filter())
async def on_cancel(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    removed = await db.cancel_booking(user_id)
    if removed:
        await callback.answer("Booking cancelled!", show_alert=True)
    else:
        await callback.answer("You don't have a booking.", show_alert=True)
    await _send_seats(callback.message, user_id=user_id, edit=True)


@router.callback_query(RefreshCallback.filter())
async def on_refresh(callback: CallbackQuery) -> None:
    await callback.answer()
    await _send_seats(callback.message, user_id=callback.from_user.id, edit=True)
