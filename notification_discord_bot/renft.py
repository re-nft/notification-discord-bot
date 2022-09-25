from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, IntEnum, unique
from typing import Callable, Optional

import discord

from notification_discord_bot.constants import (
    AVALANCHE_WHOOPI_CONTRACT_NAME,
    RENFT_BASE_URL,
    TwitterMessage,
)


@unique
class Chain(str, Enum):
    ETH = "ETH"
    MATIC = "MATIC"
    AVAX = "AVAX"


@unique
class TransactionType(str, Enum):
    LEND = "LEND"
    RENT = "RENT"


class PaymentToken(IntEnum):
    SENTINEL = 0
    WETH = 1
    DAI = 2
    USDC = 3
    USDT = 4
    TUSD = 5
    RENT = 6
    ACS = 7


EXPLORER_CHAIN_MAPPING = {
    Chain.ETH: "https://etherscan.io/address",
    Chain.MATIC: "https://polygonscan.com/address",
    Chain.AVAX: "https://snowtrace.io/address",
}


@dataclass
class NonFungibleToken:
    name: str
    nft_address: str
    token_id: str
    image_url: str
    description: str


@dataclass
class Lending:
    nft: Callable[[], NonFungibleToken]
    lending_id: int
    lender_address: str
    max_rent_duration: int
    daily_rent_price: Optional[float]
    lent_amount: int
    payment_token: PaymentToken
    collateral: Optional[float]
    lent_at: int
    upfront_rent_fee: Optional[float]

    @property
    def id(self):
        return str(self.lending_id).rjust(50, "0")


@dataclass
class Renting:
    nft: Callable[[], NonFungibleToken]
    lending_id: int
    renting_id: int
    renter_address: str
    rent_duration: int
    rented_at: int
    payment_token: PaymentToken
    collateral: Optional[float]
    daily_rent_price: Optional[float]
    lender_address: str
    upfront_rent_fee: Optional[float]

    @property
    def id(self):
        return str(self.renting_id).rjust(50, "0")


class ReNFTContract(ABC):
    @abstractmethod
    def get_lendings(self) -> list["ReNFTDatum"]:
        pass

    @abstractmethod
    def get_rentings(self) -> list["ReNFTDatum"]:
        pass

    @abstractmethod
    def is_collateral_free(self) -> bool:
        pass

    @abstractmethod
    def chain(self) -> Chain:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def query_url(self) -> str:
        pass


class ReNFTDatum(ABC):
    def __init__(self, contract: ReNFTContract, transaction_type: TransactionType):
        self.contract = contract
        self.transaction_type = transaction_type

    @abstractmethod
    def build_discord_message(self) -> discord.Embed:
        pass

    @abstractmethod
    def build_twitter_message(self) -> TwitterMessage:
        pass

    @abstractmethod
    def has_been_observed(self) -> bool:
        pass

    @abstractmethod
    def observe(self):
        pass


def get_lending_url(contract: ReNFTContract, lending_id: str | int):
    if contract.name == AVALANCHE_WHOOPI_CONTRACT_NAME:
        return f"{RENFT_BASE_URL}/collections/castle-crush?lendingId={lending_id}"
    contract_type = "collateral_free" if contract.is_collateral_free() else "collateral"
    return f"{RENFT_BASE_URL}?ctx={contract_type}&lendingId={lending_id}"


def get_profile_url(contract: ReNFTContract, address: str):
    chain = contract.chain()
    return f"{EXPLORER_CHAIN_MAPPING[chain]}/{address}"


def get_rent_duration_unit(contract: ReNFTContract) -> str:
    return "cycles" if contract.name == AVALANCHE_WHOOPI_CONTRACT_NAME else "days"
