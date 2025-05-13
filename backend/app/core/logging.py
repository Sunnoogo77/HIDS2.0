import logging
from logging.handlers import RotatingFileHandler
from app.core.config import settings
import os

LOG_PATH = "logs/hids.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

handler = RotatingFileHandler(
    LOG_PATH, maxBytes=5*1024*1024, backupCount=5
)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
handler.setFormatter(formatter)

logging.basicConfig(
    level=settings.LOG_LEVEL,
    handlers=[handler]
)
logger = logging.getLogger("hids")