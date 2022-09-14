import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Required env variables
ETHEREUM_AZRAEL_SUBGRAPH_URL = os.environ["ETHEREUM_AZRAEL_SUBGRAPH_URL"]
ETHEREUM_SYLVESTER_SUBGRAPH_URL = os.environ["ETHEREUM_SYLVESTER_SUBGRAPH_URL"]
MATIC_SYLVESTER_SUBGRAPH_URL = os.environ["MATIC_SYLVESTER_SUBGRAPH_URL"]
AVALANCHE_WHOOPI_SUBGRAPH_URL = os.environ["AVALANCHE_WHOOPI_SUBGRAPH_URL"]

NFT_PORT_API_KEY = os.environ["NFT_PORT_API_KEY"]

# Optional env variables
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

TWEEPY_API_KEY = os.getenv("TWEEPY_API_KEY")
TWEEPY_API_SECRET = os.getenv("TWEEPY_API_SECRET")
TWEEPY_ACCESS_TOKEN = os.getenv("TWEEPY_ACCESS_TOKEN")
TWEEPY_ACCESS_TOKEN_SECRET = os.getenv("TWEEPY_ACCESS_TOKEN_SECRET")


# Optional env variables with defaults
DB_PATH = os.getenv("DB_PATH", "db.json")
LOGLEVEL = os.getenv("LOGLEVEL", "INFO").upper()
F_LOGLEVEL = os.getenv("F_LOGLEVEL", "INFO").upper()
S_LOGLEVEL = os.getenv("S_LOGLEVEL", "INFO").upper()


# Static constants
RENFT_BASE_URL = "https://v2.renft.io"
SLEEP_TIME_S = 30
DEFAULT_PAGE_SIZE = 100

PRICE_BITSIZE = 32
HALF_BITSIZE = 16
BITSIZE_MAX_VALUE = 32
MAX_PRICE = 9999.9999
NUM_BITS_IN_BYTE = 8
ZEROS = "0" * 256

# Contract names

ETHEREUM_AZRAEL_CONTRACT_NAME = "Ethereum Azrael"
ETHEREUM_SYLVESTER_CONTRACT_NAME = "Ethereum Sylvester"
MATIC_SYLVESTER_CONTRACT_NAME = "Matic Sylvester"
AVALANCHE_WHOOPI_CONTRACT_NAME = "Avalanche Whoopi"
