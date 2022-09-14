from abc import ABC, abstractmethod
from enum import Enum, IntEnum, unique
from dataclasses import dataclass
from operator import attrgetter
from typing import Callable, Optional
import discord


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
    daily_rent_price: Optional[int]
    lent_amount: int
    payment_token: PaymentToken
    collateral: Optional[int]
    lent_at: int
    upfront_rent_fee: Optional[int]

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
    collateral: Optional[int]
    daily_rent_price: Optional[int]
    lender_address: str
    upfront_rent_fee: Optional[int]

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


class ReNFTDatum(ABC):
    def __init__(self, contract: ReNFTContract, transaction_type: TransactionType):
        self.contract = contract
        self.transaction_type = transaction_type

    @abstractmethod
    def build_discord_message(self) -> discord.Embed:
        pass

    @abstractmethod
    def build_twitter_message(self) -> str:
        pass

    @abstractmethod
    def has_been_observed(self) -> bool:
        pass

    @abstractmethod
    def observe(self) -> bool:
        pass


class ReNFTLendingDatum(ReNFTDatum):
    def __init__(
        self,
        contract: ReNFTContract,
        transaction_type: TransactionType,
        lending: Lending,
    ):
        super().__init__(contract, transaction_type)
        self.lending = lending

    def build_discord_message(self):
        from notification_discord_bot.utils import (
            get_lending_url,
            get_profile_url,
            get_rent_duration_unit,
        )

        nft = self.lending.nft()
        rent_duration_unit = get_rent_duration_unit(self.contract)

        msg = discord.Embed(
            title=f"{nft.name} Lent.",
            url=f"{get_lending_url(self.contract, self.lending.lending_id)}",
        )
        msg.set_thumbnail(url=nft.image_url)
        msg.add_field(
            name="Max Rent Duration",
            value=f"{self.lending.max_rent_duration} {rent_duration_unit}",
            inline=True,
        )
        if self.lending.daily_rent_price is not None:
            msg.add_field(
                name="Daily Rent Price",
                value=f"{self.lending.daily_rent_price} {self.lending.payment_token.name}",
                inline=True,
            )
        if self.lending.upfront_rent_fee is not None:
            msg.add_field(
                name="Upfront Rent Fee",
                value=f"{self.lending.upfront_rent_fee} {self.lending.payment_token.name}",
                inline=True,
            )
        if self.lending.collateral is not None:
            msg.add_field(
                name="Collateral",
                value=f"{self.lending.collateral} {self.lending.payment_token.name}",
                inline=True,
            )
        msg.add_field(
            name="Lender",
            value=f"{get_profile_url(self.contract, self.lending.lender_address)}",
            inline=False,
        )
        return msg

    def build_twitter_message(self):
        from notification_discord_bot.utils import get_lending_url, get_rent_duration_unit

        nft = self.lending.nft()
        rent_duration_unit = get_rent_duration_unit(self.contract)

        if self.lending.daily_rent_price is not None:
            msg = (
                f"{nft.name} lent for "
                f"{self.lending.daily_rent_price} {self.lending.payment_token.name} "
                f"per day for a max of {self.lending.max_rent_duration} {rent_duration_unit}. "
                f"{get_lending_url(self.contract, self.lending.lending_id)}"
            )
        else:
            msg = (
                f"{nft.name} lent for a fee of "
                f"{self.lending.upfront_rent_fee} {self.lending.payment_token.name} "
                f"for a max of {self.lending.max_rent_duration} {rent_duration_unit}. "
                f"{get_lending_url(self.contract, self.lending.lending_id)}"
            )
        return msg

    def has_been_observed(self) -> bool:
        from notification_discord_bot.models import ReNFTModel

        m = ReNFTModel.get_or_none(
            contract_name=self.contract.name,
            transaction_type=TransactionType.LEND,
        )

        return m is not None and self.lending.id <= attrgetter("renft_id")(m)

    def observe(self):
        from notification_discord_bot.models import ReNFTModel

        return ReNFTModel.update_or_create(
            contract_name=self.contract.name,
            transaction_type=TransactionType.LEND,
            defaults={"renft_id": self.lending.id},
        )


class ReNFTRentingDatum(ReNFTDatum):
    def __init__(
        self,
        contract: ReNFTContract,
        transaction_type: TransactionType,
        renting: Renting,
    ):
        super().__init__(contract, transaction_type)
        self.renting = renting

    def build_discord_message(self):
        from notification_discord_bot.utils import (
            get_profile_url,
            get_lending_url,
            get_rent_duration_unit,
        )

        nft = self.renting.nft()
        rent_duration_unit = get_rent_duration_unit(self.contract)

        msg = discord.Embed(
            title=f"{nft.name} Lent",
            url=f"{get_lending_url(self.contract, self.renting.lending_id)}",
        )
        msg.set_thumbnail(url=nft.image_url)

        msg.add_field(
            name="Rent Duration",
            value=f"{self.renting.rent_duration} {rent_duration_unit}",
            inline=True,
        )
        if self.renting.daily_rent_price is not None:
            msg.add_field(
                name="Daily Rent Price",
                value=f"{self.renting.daily_rent_price} {self.renting.payment_token.name}",
                inline=True,
            )
        if self.renting.upfront_rent_fee is not None:
            msg.add_field(
                name="Upfront Rent Fee",
                value=f"{self.renting.upfront_rent_fee} {self.renting.payment_token.name}",
                inline=True,
            )
        if self.renting.collateral is not None:
            msg.add_field(
                name="Collateral",
                value=f"{self.renting.collateral} {self.renting.payment_token.name}",
                inline=True,
            )
        msg.add_field(
            name="Lender",
            value=f"{get_profile_url(self.contract, self.renting.lender_address)}",
            inline=False,
        )
        return msg

    def build_twitter_message(self):
        from notification_discord_bot.utils import get_lending_url, get_rent_duration_unit

        nft = self.renting.nft()
        rent_duration_unit = get_rent_duration_unit(self.contract)
        if self.renting.daily_rent_price is not None:
            msg = (
                f"{nft.name} rented for "
                f"{self.renting.daily_rent_price} {self.renting.payment_token.name} "
                f"per day for {self.renting.rent_duration} {rent_duration_unit}. "
                f"{get_lending_url(self.contract, self.renting.lending_id)}"
            )
        else:
            msg = (
                f"{nft.name} rented for a fee of "
                f"{self.renting.upfront_rent_fee} {self.renting.payment_token.name} "
                f"for {self.renting.rent_duration} {rent_duration_unit}. "
                f"{get_lending_url(self.contract, self.renting.lending_id)}"
            )
        return msg

    def has_been_observed(self) -> bool:
        from notification_discord_bot.models import ReNFTModel

        m = ReNFTModel.get_or_none(
            contract_name=self.contract.name,
            transaction_type=TransactionType.RENT,
        )
        return m is not None and self.renting.id <= attrgetter("renft_id")(m)

    def observe(self):
        from notification_discord_bot.models import ReNFTModel

        if not self.has_been_observed():
            ReNFTModel.update_or_create(
                contract_name=self.contract.name,
                transaction_type=TransactionType.RENT,
                defaults={"renft_id": self.renting.id},
            )
