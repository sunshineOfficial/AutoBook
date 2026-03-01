from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class BookCallback(CallbackData, prefix="book"):
    pass


class CancelCallback(CallbackData, prefix="cancel"):
    pass


class RefreshCallback(CallbackData, prefix="refresh"):
    pass


class AdminSeatCallback(CallbackData, prefix="admin_seat"):
    seat_number: int


class KickConfirmCallback(CallbackData, prefix="kick_confirm"):
    seat_number: int


def kick_confirm_keyboard(seat_number: int, username: str | None) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    name = f"@{username}" if username else f"seat {seat_number}"
    builder.button(
        text=f"✅ Kick {name} from seat {seat_number}",
        callback_data=KickConfirmCallback(seat_number=seat_number),
    )
    builder.button(text="❌ Cancel", callback_data=RefreshCallback())
    builder.adjust(1)
    return builder


def seats_keyboard(
    seats: list[dict], user_id: int, is_admin: bool = False
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    seat_icons = {1: "1\ufe0f\u20e3", 2: "2\ufe0f\u20e3", 3: "3\ufe0f\u20e3", 4: "4\ufe0f\u20e3"}
    user_has_booking = False

    for seat in seats:
        num = seat["number"]
        icon = seat_icons.get(num, str(num))
        if seat["user_id"] is None:
            label = f"{icon} Место {num}: Свободно"
            callback = RefreshCallback()
        else:
            name = f"@{seat['username']}" if seat["username"] else f"Пользователь {seat['user_id']}"
            label = f"{icon} Место {num}: {name}"
            if seat["user_id"] == user_id:
                user_has_booking = True
            callback = AdminSeatCallback(seat_number=num) if is_admin else RefreshCallback()
        builder.button(text=label, callback_data=callback)

    builder.adjust(1)  # One seat per row

    action_builder = InlineKeyboardBuilder()
    if not is_admin:
        if user_has_booking:
            action_builder.button(text="Отменить бронирование", callback_data=CancelCallback())
        else:
            action_builder.button(text="Забронировать место", callback_data=BookCallback())
    action_builder.button(text="Обновить", callback_data=RefreshCallback())
    action_builder.adjust(2)

    builder.attach(action_builder)
    return builder
