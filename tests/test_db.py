import pytest
from unittest.mock import patch

import bot.db as db_module


@pytest.fixture
async def tmp_db(tmp_path):
    db_file = str(tmp_path / "test.db")
    with patch("bot.db.DB_PATH", db_file):
        await db_module.init_db()
        yield db_module


async def test_kick_user_by_seat_returns_user_id(tmp_db):
    await tmp_db.book_seat(42, "alice")
    seats = await tmp_db.get_all_seats()
    booked_seat = next(s for s in seats if s["user_id"] == 42)

    result = await tmp_db.kick_user_by_seat(booked_seat["number"])

    assert result == 42
    seats_after = await tmp_db.get_all_seats()
    assert all(s["user_id"] is None for s in seats_after)


async def test_kick_user_by_seat_returns_none_for_free_seat(tmp_db):
    result = await tmp_db.kick_user_by_seat(1)
    assert result is None
