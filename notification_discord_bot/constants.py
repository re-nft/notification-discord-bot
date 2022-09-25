import os

from dotenv import load_dotenv

load_dotenv()

# Required env variables
ETHEREUM_AZRAEL_SUBGRAPH_URL = os.getenv("ETHEREUM_AZRAEL_SUBGRAPH_URL")
ETHEREUM_SYLVESTER_SUBGRAPH_URL = os.getenv("ETHEREUM_SYLVESTER_SUBGRAPH_URL")
MATIC_SYLVESTER_SUBGRAPH_URL = os.getenv("MATIC_SYLVESTER_SUBGRAPH_URL")
AVALANCHE_WHOOPI_SUBGRAPH_URL = os.getenv("AVALANCHE_WHOOPI_SUBGRAPH_URL")

ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")

# Optional env variables
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

TWEEPY_API_KEY = os.getenv("TWEEPY_API_KEY")
TWEEPY_API_SECRET = os.getenv("TWEEPY_API_SECRET")
TWEEPY_ACCESS_TOKEN = os.getenv("TWEEPY_ACCESS_TOKEN")
TWEEPY_ACCESS_TOKEN_SECRET = os.getenv("TWEEPY_ACCESS_TOKEN_SECRET")

NFT_PORT_API_KEY = os.getenv("NFT_PORT_API_KEY")

# Optional env variables with defaults
DB_PATH = os.getenv("DB_PATH", "db.json")
LOGLEVEL = os.getenv("LOGLEVEL", "INFO").upper()
F_LOGLEVEL = os.getenv("F_LOGLEVEL", "INFO").upper()
S_LOGLEVEL = os.getenv("S_LOGLEVEL", "INFO").upper()


# Static constants
RENFT_BASE_URL = "https://v2.renft.io"
IPFS_GATEWAY_URL = "https://ipfs.io/ipfs"
ETHEREUM_ALCHEMY_BASE_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
POLYGON_ALCHEMY_BASE_URL = f"https://polygon-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
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
