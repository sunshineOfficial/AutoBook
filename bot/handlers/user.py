from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from bot import db
from bot.config import ADMIN_ID
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
        text = "\U0001f6ab Машина сейчас недоступна."
        if edit:
            await message.edit_text(text, reply_markup=None)
        else:
            await message.answer(text)
        return

    seats = await db.get_all_seats()
    free = sum(1 for s in seats if s["user_id"] is None)

    seat_icons = {1: "1\ufe0f\u20e3", 2: "2\ufe0f\u20e3", 3: "3\ufe0f\u20e3", 4: "4\ufe0f\u20e3"}
    lines = [f"\U0001f697 Места в машине ({free} свободно):\n"]
    for seat in seats:
        num = seat["number"]
        icon = seat_icons.get(num, str(num))
        if seat["user_id"] is None:
            lines.append(f"{icon} Место {num}: Свободно")
        else:
            name = f"@{seat['username']}" if seat["username"] else f"Пользователь {seat['user_id']}"
            lines.append(f"{icon} Место {num}: {name}")

    text = "\n".join(lines)
    kb = seats_keyboard(seats, user_id, is_admin=(user_id == ADMIN_ID))

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
        "\U0001f44b Добро пожаловать в AutoBook!\n\n"
        "Я помогаю проверять и бронировать места в машине.\n\n"
        "Используйте /seats, чтобы увидеть свободные места и забронировать одно."
    )


@router.message(Command("seats"))
async def cmd_seats(message: Message) -> None:
    await _send_seats(message, user_id=message.from_user.id)


@router.callback_query(BookCallback.filter())
async def on_book(callback: CallbackQuery) -> None:
    available = await db.is_car_available()
    if not available:
        await callback.answer("\U0001f6ab Машина сейчас недоступна.", show_alert=True)
        return

    user_id = callback.from_user.id
    username = callback.from_user.username
    seat = await db.book_seat(user_id, username)

    if seat is None:
        seats = await db.get_all_seats()
        user_booked = any(s["user_id"] == user_id for s in seats)
        if user_booked:
            await callback.answer("У вас уже есть бронирование!", show_alert=True)
        else:
            await callback.answer("Нет свободных мест.", show_alert=True)
        return

    await callback.answer(f"Место {seat} забронировано!", show_alert=True)
    name = f"@{username}" if username else f"Пользователь {user_id}"
    try:
        await callback.bot.send_message(ADMIN_ID, f"✅ {name} забронировал место {seat}")
    except Exception:
        pass  # Notification failure must not interrupt the user flow
    await _send_seats(callback.message, user_id=user_id, edit=True)


@router.callback_query(CancelCallback.filter())
async def on_cancel(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    freed_seat = await db.cancel_booking(user_id)
    if freed_seat is not None:
        await callback.answer("Бронирование отменено!", show_alert=True)
        username = callback.from_user.username
        name = f"@{username}" if username else f"Пользователь {user_id}"
        try:
            await callback.bot.send_message(ADMIN_ID, f"❌ {name} отменил место {freed_seat}")
        except Exception:
            pass  # Notification failure must not interrupt the user flow
    else:
        await callback.answer("У вас нет бронирования.", show_alert=True)
    await _send_seats(callback.message, user_id=user_id, edit=True)


@router.callback_query(RefreshCallback.filter())
async def on_refresh(callback: CallbackQuery) -> None:
    await callback.answer()
    await _send_seats(callback.message, user_id=callback.from_user.id, edit=True)
