from abc import ABC, abstractmethod
from functools import partial
from operator import attrgetter
from typing import Any
from notification_discord_bot.constants import DEFAULT_PAGE_SIZE
from notification_discord_bot import mixins
from notification_discord_bot.nft import get_nft
from notification_discord_bot.renft import (
    Chain,
    Lending,
    PaymentToken,
    Renting,
    ReNFTContract,
    ReNFTDatum,
    ReNFTLendingDatum,
    ReNFTRentingDatum,
    TransactionType,
)
from notification_discord_bot.utils import query_the_graph
from notification_discord_bot.queries import (
    AZRAEL_GET_LENDINGS_QUERY,
    AZRAEL_GET_RENTINGS_QUERY,
    SYLVESTER_GET_LENDINGS_QUERY,
    SYLVESTER_GET_RENTINGS_QUERY,
    WHOOPI_GET_LENDINGS_QUERY,
    WHOOPI_GET_RENTINGS_QUERY,
)


class AzraelContract(ReNFTContract, mixins.BlockchainContractMixin):
    name = "Azrael"

    def transform_lending(self, lending: dict[str, Any]) -> ReNFTLendingDatum:
        transaction_type = TransactionType.LEND
        nft = partial(get_nft, lending["nftAddress"], lending["tokenId"], self.chain())
        _lending = Lending(
            nft=nft,
            lending_id=int(lending["id"]),
            lender_address=lending["lenderAddress"],
            max_rent_duration=lending["maxRentDuration"],
            daily_rent_price=lending["dailyRentPrice"],
            lent_amount=lending["lentAmount"],
            payment_token=PaymentToken(int(lending["paymentToken"])),
            collateral=lending["nftPrice"],
            lent_at=lending["lentAt"],
            upfront_rent_fee=None,
        )
        return ReNFTLendingDatum(self, transaction_type, _lending)

    def transform_renting(self, renting: dict[str, Any]) -> ReNFTRentingDatum:
        transaction_type = TransactionType.RENT
        nft = partial(
            get_nft,
            renting["lending"]["nftAddress"],
            renting["lending"]["tokenId"],
            self.chain(),
        )
        _renting = Renting(
            nft=nft,
            lending_id=renting["lending"]["id"],
            renting_id=renting["id"],
            renter_address=renting["renterAddress"],
            rent_duration=renting["rentDuration"],
            rented_at=renting["rentedAt"],
            payment_token=PaymentToken(int(renting["lending"]["paymentToken"])),
            collateral=renting["lending"]["nftPrice"],
            daily_rent_price=renting["lending"]["dailyRentPrice"],
            lender_address=renting["lending"]["lenderAddress"],
            upfront_rent_fee=None,
        )
        return ReNFTRentingDatum(self, transaction_type, _renting)

    def get_lendings(self, page=0) -> list[ReNFTDatum]:
        data = query_the_graph(
            self.query_url, AZRAEL_GET_LENDINGS_QUERY, skip=page * DEFAULT_PAGE_SIZE
        )
        lendings = data.get("data", {}).get("lendings", [])
        return [self.transform_lending(l) for l in lendings]

    def get_rentings(self, page=0) -> list[ReNFTDatum]:
        data = query_the_graph(
            self.query_url, AZRAEL_GET_RENTINGS_QUERY, skip=page * DEFAULT_PAGE_SIZE
        )
        rentings = data.get("data", {}).get("rentings", [])
        return [self.transform_renting(r) for r in rentings]

    def is_collateral_free(self) -> bool:
        return False


class SylvesterContract(ReNFTContract, mixins.BlockchainContractMixin):
    name = "Sylvester"

    def transform_lending(self, lending: dict[str, Any]) -> ReNFTLendingDatum:
        transaction_type = TransactionType.LEND
        nft = partial(get_nft, lending["nftAddress"], lending["tokenID"], self.chain())
        _lending = Lending(
            nft=nft,
            lending_id=int(lending["id"]),
            lender_address=lending["lenderAddress"],
            max_rent_duration=lending["maxRentDuration"],
            daily_rent_price=lending["dailyRentPrice"],
            lent_amount=lending["lendAmount"],
            payment_token=PaymentToken(int(lending["paymentToken"])),
            collateral=None,
            lent_at=lending["lentAt"],
            upfront_rent_fee=None,
        )
        return ReNFTLendingDatum(self, transaction_type, _lending)

    def transform_renting(self, renting: dict[str, Any]) -> ReNFTRentingDatum:
        transaction_type = TransactionType.RENT
        nft = partial(
            get_nft,
            renting["lending"]["nftAddress"],
            renting["lending"]["tokenID"],
            self.chain(),
        )
        _renting = Renting(
            nft=nft,
            lending_id=renting["lending"]["id"],
            renting_id=renting["id"],
            renter_address=renting["renterAddress"],
            rent_duration=renting["rentDuration"],
            rented_at=renting["rentedAt"],
            payment_token=PaymentToken(int(renting["lending"]["paymentToken"])),
            collateral=None,
            daily_rent_price=renting["lending"]["dailyRentPrice"],
            lender_address=renting["lending"]["lenderAddress"],
            upfront_rent_fee=None,
        )
        return ReNFTRentingDatum(self, transaction_type, _renting)

    def get_lendings(self, page=0) -> list[ReNFTDatum]:
        data = query_the_graph(
            self.query_url, SYLVESTER_GET_LENDINGS_QUERY, skip=page * DEFAULT_PAGE_SIZE
        )
        lendings = data.get("data", {}).get("lendings", [])
        return [self.transform_lending(l) for l in lendings]

    def get_rentings(self, page=0) -> list[ReNFTDatum]:
        data = query_the_graph(
            self.query_url, SYLVESTER_GET_RENTINGS_QUERY, skip=page * DEFAULT_PAGE_SIZE
        )
        rentings = data.get("data", {}).get("rentings", [])
        return [self.transform_renting(r) for r in rentings]

    def is_collateral_free(self) -> bool:
        return True


class WhoopiContract(ReNFTContract, mixins.BlockchainContractMixin):
    name = "Whoopi"

    def transform_lending(self, lending: dict[str, Any]) -> ReNFTLendingDatum:
        transaction_type = TransactionType.LEND
        nft = partial(get_nft, lending["nftAddress"], lending["tokenId"], self.chain())
        _lending = Lending(
            nft=nft,
            lending_id=int(lending["id"]),
            lender_address=lending["lenderAddress"],
            max_rent_duration=lending["maxRentDuration"],
            daily_rent_price=None,
            lent_amount=1,
            payment_token=PaymentToken(int(lending["paymentToken"])),
            collateral=None,
            lent_at=lending["lentAt"],
            upfront_rent_fee=lending["upfrontRentFee"],
        )
        return ReNFTLendingDatum(self, transaction_type, _lending)

    def transform_renting(self, renting: dict[str, Any]) -> ReNFTRentingDatum:
        transaction_type = TransactionType.RENT
        nft = partial(
            get_nft,
            renting["lending"]["nftAddress"],
            renting["lending"]["tokenId"],
            self.chain(),
        )
        _renting = Renting(
            nft=nft,
            lending_id=renting["lending"]["id"],
            renting_id=renting["id"],
            renter_address=renting["renterAddress"],
            rent_duration=renting["rentDuration"],
            rented_at=renting["rentedAt"],
            payment_token=PaymentToken(int(renting["lending"]["paymentToken"])),
            collateral=None,
            daily_rent_price=None,
            lender_address=renting["lending"]["lenderAddress"],
            upfront_rent_fee=renting["lending"]["upfrontRentFee"],
        )
        return ReNFTRentingDatum(self, transaction_type, _renting)

    def get_lendings(self, page=0) -> list[ReNFTDatum]:
        data = query_the_graph(
            self.query_url, WHOOPI_GET_LENDINGS_QUERY, skip=page * DEFAULT_PAGE_SIZE
        )
        lendings = data.get("data", {}).get("lendings", [])
        return [self.transform_lending(l) for l in lendings]

    def get_rentings(self, page=0) -> list[ReNFTDatum]:
        data = query_the_graph(
            self.query_url, WHOOPI_GET_RENTINGS_QUERY, skip=page * DEFAULT_PAGE_SIZE
        )
        rentings = data.get("data", {}).get("rentings", [])
        return [self.transform_renting(r) for r in rentings]

    def is_collateral_free(self) -> bool:
        return True


class EthereumAzraelContract(mixins.EthereumAzraelMixin, AzraelContract):
    name = "Ethereum Azrael"

    def chain(self) -> Chain:
        return Chain.ETH


class EthereumSylvesterContract(mixins.EthereumSylvesterMixin, SylvesterContract):
    name = "Ethereum Sylvester"

    def chain(self) -> Chain:
        return Chain.ETH


class MaticSylvesterContract(mixins.MaticSylvesterMixin, SylvesterContract):
    name = "Matic Sylvester"

    def chain(self) -> Chain:
        return Chain.MATIC


class AvalancheWhoopiContract(mixins.AvalancheWhoopiMixin, WhoopiContract):
    name = "Avalanche Whoopi"

    def chain(self) -> Chain:
        return Chain.AVAX


all_contracts = [
    EthereumAzraelContract(),
    EthereumSylvesterContract(),
    MaticSylvesterContract(),
    AvalancheWhoopiContract(),
]
