import logging
import os
import sys
import time

import telegram.ext as tg
from aiohttp import ClientSession
-from arq import Arq
+from Python_ARQ import ARQ
from redis import StrictRedis
from pyrogram import Client
from telethon import TelegramClient

StartTime = time.time()

# ================= LOGGING ================= #

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

LOGGER = logging.getLogger(__name__)

# ================= PYTHON VERSION ================= #

if sys.version_info < (3, 8):
    LOGGER.error("Python 3.8+ is required. Bot is quitting.")
    sys.exit(1)

# ================= ENV ================= #

def strtobool(val):
    return str(val).lower() in ("true", "1", "yes", "y")

ENV = strtobool(os.environ.get("ENV", False))

if ENV:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    TOKEN = os.environ.get("TOKEN")

    ALLOW_CHATS = strtobool(os.environ.get("ALLOW_CHATS", True))
    ALLOW_EXCL = strtobool(os.environ.get("ALLOW_EXCL", False))
    DEL_CMDS = strtobool(os.environ.get("DEL_CMDS", False))
    INFOPIC = strtobool(os.environ.get("INFOPIC", True))
    STRICT_GBAN = strtobool(os.environ.get("STRICT_GBAN", True))

    CASH_API_KEY = os.environ.get("CASH_API_KEY")
    DB_URI = os.environ.get("DATABASE_URL")
    EVENT_LOGS = os.environ.get("EVENT_LOGS")

    LOAD = os.environ.get("LOAD", "").split()
    NO_LOAD = os.environ.get("NO_LOAD", "").split()

    MONGO_DB_URI = os.environ.get("MONGO_DB_URI")
    REDIS_URL = os.environ.get("REDIS_URL")

    START_IMG = os.environ.get(
        "START_IMG", "https://telegra.ph/file/40eb1ed850cdea274693e.jpg"
    )
    PM_START_IMG = os.environ.get("PM_START_IMG")
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "Gojo_support_chat")
    TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TEMP_DOWNLOAD_DIRECTORY", "./")

    TIME_API_KEY = os.environ.get("TIME_API_KEY")
    WORKERS = int(os.environ.get("WORKERS", 8))

    OWNER_ID = int(os.environ.get("OWNER_ID"))

    BL_CHATS = set(map(int, os.environ.get("BL_CHATS", "").split()))
    DRAGONS = set(map(int, os.environ.get("DRAGONS", "").split()))
    DEV_USERS = set(map(int, os.environ.get("DEV_USERS", "").split()))
    DEMONS = set(map(int, os.environ.get("DEMONS", "").split()))
    TIGERS = set(map(int, os.environ.get("TIGERS", "").split()))
    WOLVES = set(map(int, os.environ.get("WOLVES", "").split()))

    # ARQ
   -    arq = Arq(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)
   +    arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

else:
    raise RuntimeError("ENV must be enabled on Heroku")

# ================= USERS ================= #

DRAGONS.update(
    {
        OWNER_ID,
        6432025901,
        6058139652,
        6864672519,
        6944225218,
        6438969887,
    }
)

DEV_USERS.update({OWNER_ID, 6171176459, 6058139652})

# ================= REDIS ================= #

REDIS = StrictRedis.from_url(REDIS_URL, decode_responses=True)

try:
    REDIS.ping()
    LOGGER.info("[Sagiri]: Redis connected successfully")
except Exception as e:
    raise RuntimeError("Redis is not reachable") from e

# ================= CLIENTS ================= #

updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher

telethn = TelegramClient("Sagiri", API_ID, API_HASH)
pbot = Client("SagiriRobot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

aiohttpsession = ClientSession()

BOT_ID = dispatcher.bot.id
BOT_NAME = dispatcher.bot.first_name
BOT_USERNAME = dispatcher.bot.username

# ================= ARQ CLIENT ================= #

if not ARQ_API_KEY:
    LOGGER.warning("ARQ API key not set, ARQ features disabled")
    arq = None
else:
    arq = Arq(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)
    LOGGER.info("[Sagiri]: ARQ client initialized")

# ================= LIST FINALIZE ================= #

DRAGONS = list(DRAGONS | DEV_USERS)
DEV_USERS = list(DEV_USERS)
WOLVES = list(WOLVES)
DEMONS = list(DEMONS)
TIGERS = list(TIGERS)

# ================= HANDLERS ================= #

from SagiriRobot.modules.helper_funcs.handlers import (
    CustomCommandHandler,
    CustomMessageHandler,
    CustomRegexHandler,
)

tg.RegexHandler = CustomRegexHandler
tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
