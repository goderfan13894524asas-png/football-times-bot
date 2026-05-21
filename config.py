import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@footballtimes_official")
CHANNEL_LINK = "https://ble.ir/footballtimes_official"

DEFAULT_MAIN_ADMIN_IDS = [994865959, 324157864]
DEFAULT_SUPPORT_ADMINS = [890352247, 1050936429]

PRICE_PER_DAY = 5000

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "football_bot"
}