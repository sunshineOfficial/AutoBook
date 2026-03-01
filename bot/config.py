import os
import sys

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    sys.exit("Error: BOT_TOKEN is not set. Check your .env file.")

_admin_id = os.getenv("ADMIN_ID")
if not _admin_id:
    sys.exit("Error: ADMIN_ID is not set. Check your .env file.")

ADMIN_ID = int(_admin_id)
