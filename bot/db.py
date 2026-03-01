import aiosqlite
from datetime import datetime, timezone

DB_PATH = "autobook.db"

TOTAL_SEATS = 4


def _connect() -> aiosqlite.Connection:
    conn = aiosqlite.connect(DB_PATH)
    return conn


async def init_db() -> None:
    async with _connect() as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            "CREATE TABLE IF NOT EXISTS settings "
            "(key TEXT PRIMARY KEY, value TEXT)"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS bookings "
            "(seat_number INTEGER PRIMARY KEY, "
            "user_id INTEGER, username TEXT, booked_at TEXT)"
        )
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES ('car_available', '1')"
        )
        await db.commit()


async def get_all_seats() -> list[dict]:
    async with _connect() as db:
        db.row_factory = aiosqlite.Row
        seats = []
        for num in range(1, TOTAL_SEATS + 1):
            cursor = await db.execute(
                "SELECT user_id, username FROM bookings WHERE seat_number = ?",
                (num,),
            )
            row = await cursor.fetchone()
            if row:
                seats.append(
                    {"number": num, "user_id": row["user_id"], "username": row["username"]}
                )
            else:
                seats.append({"number": num, "user_id": None, "username": None})
        return seats


async def book_seat(user_id: int, username: str | None) -> int | None:
    async with _connect() as db:
        db.row_factory = aiosqlite.Row
        # Check if user already has a booking
        cursor = await db.execute(
            "SELECT seat_number FROM bookings WHERE user_id = ?", (user_id,)
        )
        if await cursor.fetchone():
            return None

        # Find first free seat
        booked = await db.execute("SELECT seat_number FROM bookings")
        booked_nums = {row["seat_number"] for row in await booked.fetchall()}

        for num in range(1, TOTAL_SEATS + 1):
            if num not in booked_nums:
                await db.execute(
                    "INSERT INTO bookings (seat_number, user_id, username, booked_at) "
                    "VALUES (?, ?, ?, ?)",
                    (num, user_id, username, datetime.now(timezone.utc).isoformat()),
                )
                await db.commit()
                return num
        return None


async def cancel_booking(user_id: int) -> int | None:
    async with _connect() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT seat_number FROM bookings WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        seat_number = row["seat_number"]
        await db.execute("DELETE FROM bookings WHERE user_id = ?", (user_id,))
        await db.commit()
        return seat_number


async def clear_all_bookings() -> None:
    async with _connect() as db:
        await db.execute("DELETE FROM bookings")
        await db.commit()


async def kick_user(user_id: int) -> int | None:
    return await cancel_booking(user_id)


async def is_car_available() -> bool:
    async with _connect() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT value FROM settings WHERE key = 'car_available'"
        )
        row = await cursor.fetchone()
        return row is not None and row["value"] == "1"


async def toggle_car_available() -> bool:
    current = await is_car_available()
    new_value = "0" if current else "1"
    async with _connect() as db:
        await db.execute(
            "UPDATE settings SET value = ? WHERE key = 'car_available'",
            (new_value,),
        )
        await db.commit()
    return not current
