from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import CallbackQuery

from bot import db
from bot.config import ADMIN_ID
from bot.handlers.user import _send_seats
from bot.keyboards import AdminSeatCallback, KickConfirmCallback, kick_confirm_keyboard

router = Router()
router.message.filter(F.from_user.id == ADMIN_ID)
router.callback_query.filter(F.from_user.id == ADMIN_ID)


@router.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    await db.clear_all_bookings()
    await message.answer("\u2705 Все бронирования удалены.")


@router.message(Command("kick"))
async def cmd_kick(message: Message) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /kick <user_id или @username>")
        return

    target = args[1].strip()

    # Try to parse as user_id
    if target.isdigit():
        user_id = int(target)
        removed = await db.kick_user(user_id)
        if removed:
            await message.answer(f"\u2705 Бронирование пользователя {user_id} удалено.")
        else:
            await message.answer(f"Бронирование для пользователя {user_id} не найдено.")
        return

    # Try to match by username
    username = target.lstrip("@")
    seats = await db.get_all_seats()
    for seat in seats:
        if seat["username"] and seat["username"].lower() == username.lower():
            await db.kick_user(seat["user_id"])
            await message.answer(f"\u2705 Бронирование @{username} удалено.")
            return

    await message.answer(f"Бронирование для {target} не найдено.")


@router.message(Command("toggle"))
async def cmd_toggle(message: Message) -> None:
    new_state = await db.toggle_car_available()
    status = "доступна \U0001f7e2" if new_state else "недоступна \U0001f534"
    await message.answer(f"Машина теперь {status}.")


@router.callback_query(AdminSeatCallback.filter())
async def on_admin_seat(callback: CallbackQuery, callback_data: AdminSeatCallback) -> None:
    seats = await db.get_all_seats()
    seat = next((s for s in seats if s["number"] == callback_data.seat_number), None)
    if seat is None or seat["user_id"] is None:
        await callback.answer()
        await _send_seats(callback.message, user_id=ADMIN_ID, edit=True)
        return
    confirm_kb = kick_confirm_keyboard(callback_data.seat_number, seat["username"])
    await callback.message.edit_reply_markup(reply_markup=confirm_kb.as_markup())
    await callback.answer()


@router.callback_query(KickConfirmCallback.filter())
async def on_kick_confirm(callback: CallbackQuery, callback_data: KickConfirmCallback) -> None:
    evicted_user_id = await db.kick_user_by_seat(callback_data.seat_number)
    if evicted_user_id is not None:
        await callback.answer("✅ Kicked", show_alert=True)
    else:
        await callback.answer("Seat already free.", show_alert=True)
    await _send_seats(callback.message, user_id=ADMIN_ID, edit=True)
