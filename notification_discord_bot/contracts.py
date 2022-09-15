from functools import partial
from typing import Any, ClassVar

from notification_discord_bot.constants import (
    AVALANCHE_WHOOPI_CONTRACT_NAME,
    AVALANCHE_WHOOPI_SUBGRAPH_URL,
    DEFAULT_PAGE_SIZE,
    ETHEREUM_AZRAEL_CONTRACT_NAME,
    ETHEREUM_AZRAEL_SUBGRAPH_URL,
    ETHEREUM_SYLVESTER_CONTRACT_NAME,
    ETHEREUM_SYLVESTER_SUBGRAPH_URL,
    MATIC_SYLVESTER_CONTRACT_NAME,
    MATIC_SYLVESTER_SUBGRAPH_URL,
)
from notification_discord_bot.currency import format_fixed, unpack_price
from notification_discord_bot.data import ReNFTLendingDatum, ReNFTRentingDatum
from notification_discord_bot.nft import get_nft
from notification_discord_bot.queries import (
    AZRAEL_GET_LENDINGS_QUERY,
    AZRAEL_GET_RENTINGS_QUERY,
    SYLVESTER_GET_LENDINGS_QUERY,
    SYLVESTER_GET_RENTINGS_QUERY,
    WHOOPI_GET_LENDINGS_QUERY,
    WHOOPI_GET_RENTINGS_QUERY,
)
from notification_discord_bot.renft import (
    Chain,
    Lending,
    PaymentToken,
    ReNFTContract,
    ReNFTDatum,
    Renting,
    TransactionType,
)
from notification_discord_bot.resolvers import RESOLVERS, PaymentTokenDetails
from notification_discord_bot.utils import query_the_graph


def resolve_payment_token_details(
    contract: ReNFTContract, token: PaymentToken
) -> PaymentTokenDetails:
    return RESOLVERS[contract.name][token]


class AzraelContract(ReNFTContract):
    def transform_lending(self, lending: dict[str, Any]) -> ReNFTLendingDatum:
        transaction_type = TransactionType.LEND
        nft = partial(get_nft, lending["nftAddress"], lending["tokenId"], self.chain())
        _lending = Lending(
            nft=nft,
            lending_id=int(lending["id"]),
            lender_address=lending["lenderAddress"],
            max_rent_duration=lending["maxRentDuration"],
            daily_rent_price=unpack_price(lending["dailyRentPrice"]),
            lent_amount=lending["lentAmount"],
            payment_token=PaymentToken(int(lending["paymentToken"])),
            collateral=unpack_price(lending["nftPrice"]),
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
            collateral=unpack_price(renting["lending"]["nftPrice"]),
            daily_rent_price=unpack_price(renting["lending"]["dailyRentPrice"]),
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


class SylvesterContract(ReNFTContract):
    def transform_lending(self, lending: dict[str, Any]) -> ReNFTLendingDatum:
        transaction_type = TransactionType.LEND
        nft = partial(get_nft, lending["nftAddress"], lending["tokenID"], self.chain())
        _lending = Lending(
            nft=nft,
            lending_id=int(lending["id"]),
            lender_address=lending["lenderAddress"],
            max_rent_duration=lending["maxRentDuration"],
            daily_rent_price=unpack_price(lending["dailyRentPrice"]),
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
            daily_rent_price=unpack_price(renting["lending"]["dailyRentPrice"]),
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


class WhoopiContract(ReNFTContract):
    def transform_lending(self, lending: dict[str, Any]) -> ReNFTLendingDatum:
        transaction_type = TransactionType.LEND
        nft = partial(get_nft, lending["nftAddress"], lending["tokenId"], self.chain())
        payment_token = PaymentToken(int(lending["paymentToken"]))
        payment_token_details = resolve_payment_token_details(self, payment_token)
        _lending = Lending(
            nft=nft,
            lending_id=int(lending["id"]),
            lender_address=lending["lenderAddress"],
            max_rent_duration=lending["maxRentDuration"],
            daily_rent_price=None,
            lent_amount=1,
            payment_token=payment_token,
            collateral=None,
            lent_at=lending["lentAt"],
            upfront_rent_fee=float(
                format_fixed(
                    int(lending["upfrontRentFee"]), payment_token_details.scale
                )
            ),
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
        payment_token = PaymentToken(int(renting["lending"]["paymentToken"]))
        payment_token_details = resolve_payment_token_details(self, payment_token)
        _renting = Renting(
            nft=nft,
            lending_id=renting["lending"]["id"],
            renting_id=renting["id"],
            renter_address=renting["renterAddress"],
            rent_duration=renting["rentDuration"],
            rented_at=renting["rentedAt"],
            payment_token=payment_token,
            collateral=None,
            daily_rent_price=None,
            lender_address=renting["lending"]["lenderAddress"],
            upfront_rent_fee=float(
                format_fixed(
                    int(renting["lending"]["upfrontRentFee"]),
                    payment_token_details.scale,
                )
            ),
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


class EthereumAzraelContract(AzraelContract):
    name = ETHEREUM_AZRAEL_CONTRACT_NAME
    query_url: ClassVar[str] = ETHEREUM_AZRAEL_SUBGRAPH_URL

    def chain(self) -> Chain:
        return Chain.ETH


class EthereumSylvesterContract(SylvesterContract):
    name = ETHEREUM_SYLVESTER_CONTRACT_NAME
    query_url: ClassVar[str] = ETHEREUM_SYLVESTER_SUBGRAPH_URL

    def chain(self) -> Chain:
        return Chain.ETH


class MaticSylvesterContract(SylvesterContract):
    name = MATIC_SYLVESTER_CONTRACT_NAME
    query_url: ClassVar[str] = MATIC_SYLVESTER_SUBGRAPH_URL

    def chain(self) -> Chain:
        return Chain.MATIC


class AvalancheWhoopiContract(WhoopiContract):
    name = AVALANCHE_WHOOPI_CONTRACT_NAME
    query_url: ClassVar[str] = AVALANCHE_WHOOPI_SUBGRAPH_URL

    def chain(self) -> Chain:
        return Chain.AVAX


all_contracts = [
    EthereumAzraelContract(),
    EthereumSylvesterContract(),
    MaticSylvesterContract(),
    AvalancheWhoopiContract(),
]
