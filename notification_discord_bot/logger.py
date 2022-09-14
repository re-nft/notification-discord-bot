import logging
import sys
from notification_discord_bot.constants import F_LOGLEVEL, LOGLEVEL, S_LOGLEVEL

logger = logging.getLogger("ReNFTLogger")
logger.setLevel(LOGLEVEL)

formatter = logging.Formatter(
    "%(process)d |:| %(levelname)s |:| %(asctime)s.%(msecs)03d |:| %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

f_handler = logging.FileHandler(filename="notification_discord_bot.log", encoding="utf-8")
f_handler.setLevel(F_LOGLEVEL)
f_handler.setFormatter(formatter)
logger.addHandler(f_handler)

s_handler = logging.StreamHandler(sys.stdout)
s_handler.setLevel(S_LOGLEVEL)
s_handler.setFormatter(formatter)
logger.addHandler(s_handler)
