from bot.keyboards import (
    AdminSeatCallback,
    BookCallback,
    CancelCallback,
    KickConfirmCallback,
    RefreshCallback,
    kick_confirm_keyboard,
    seats_keyboard,
)


def make_seats(booked_user_id=None):
    return [
        {"number": 1, "user_id": booked_user_id, "username": "alice" if booked_user_id else None},
        {"number": 2, "user_id": None, "username": None},
    ]


def test_admin_sees_admin_seat_callback_for_booked_seat():
    seats = make_seats(booked_user_id=42)
    kb = seats_keyboard(seats, user_id=999, is_admin=True)
    markup = kb.as_markup()
    booked_button = markup.inline_keyboard[0][0]
    assert booked_button.callback_data == AdminSeatCallback(seat_number=1).pack()


def test_admin_sees_refresh_callback_for_free_seat():
    seats = make_seats(booked_user_id=None)
    kb = seats_keyboard(seats, user_id=999, is_admin=True)
    markup = kb.as_markup()
    free_button = markup.inline_keyboard[0][0]
    assert free_button.callback_data == RefreshCallback().pack()


def test_regular_user_sees_refresh_callback_for_booked_seat():
    seats = make_seats(booked_user_id=42)
    kb = seats_keyboard(seats, user_id=999, is_admin=False)
    markup = kb.as_markup()
    booked_button = markup.inline_keyboard[0][0]
    assert booked_button.callback_data == RefreshCallback().pack()


def test_regular_user_with_booking_sees_cancel_button():
    seats = make_seats(booked_user_id=999)
    kb = seats_keyboard(seats, user_id=999, is_admin=False)
    markup = kb.as_markup()
    action_row = markup.inline_keyboard[-1]
    labels = [btn.text for btn in action_row]
    assert any("Отменить" in label for label in labels)


def test_admin_does_not_see_book_or_cancel_buttons():
    seats = make_seats(booked_user_id=42)
    kb = seats_keyboard(seats, user_id=42, is_admin=True)
    markup = kb.as_markup()
    all_labels = [btn.text for row in markup.inline_keyboard for btn in row]
    assert not any("Забронировать" in label or "Отменить" in label for label in all_labels)


def test_kick_confirm_keyboard_with_username():
    kb = kick_confirm_keyboard(seat_number=1, username="alice")
    markup = kb.as_markup()
    confirm_btn = markup.inline_keyboard[0][0]
    cancel_btn = markup.inline_keyboard[1][0]
    assert confirm_btn.callback_data == KickConfirmCallback(seat_number=1).pack()
    assert "@alice" in confirm_btn.text
    assert cancel_btn.callback_data == RefreshCallback().pack()


def test_kick_confirm_keyboard_without_username():
    kb = kick_confirm_keyboard(seat_number=2, username=None)
    markup = kb.as_markup()
    confirm_btn = markup.inline_keyboard[0][0]
    assert "место 2" in confirm_btn.text
