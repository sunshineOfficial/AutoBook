from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class BookCallback(CallbackData, prefix="book"):
    pass


class CancelCallback(CallbackData, prefix="cancel"):
    pass


class RefreshCallback(CallbackData, prefix="refresh"):
    pass


def seats_keyboard(
    seats: list[dict], user_id: int
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    seat_icons = {1: "1\ufe0f\u20e3", 2: "2\ufe0f\u20e3", 3: "3\ufe0f\u20e3", 4: "4\ufe0f\u20e3"}
    user_has_booking = False

    for seat in seats:
        num = seat["number"]
        icon = seat_icons.get(num, str(num))
        if seat["user_id"] is None:
            label = f"{icon} Seat {num}: Free"
        else:
            name = f"@{seat['username']}" if seat["username"] else f"User {seat['user_id']}"
            label = f"{icon} Seat {num}: {name}"
            if seat["user_id"] == user_id:
                user_has_booking = True
        builder.button(text=label, callback_data=RefreshCallback())

    builder.adjust(1)  # One seat per row

    action_builder = InlineKeyboardBuilder()
    if user_has_booking:
        action_builder.button(text="Cancel my booking", callback_data=CancelCallback())
    else:
        action_builder.button(text="Book a seat", callback_data=BookCallback())
    action_builder.button(text="Refresh", callback_data=RefreshCallback())
    action_builder.adjust(2)

    builder.attach(action_builder)
    return builder
