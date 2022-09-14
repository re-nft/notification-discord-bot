from operator import attrgetter

from notification_discord_bot.models import ReNFTModel
from notification_discord_bot.renft import (
    Lending,
    ReNFTContract,
    ReNFTDatum,
    Renting,
    TransactionType,
    get_lending_url,
    get_profile_url,
    get_rent_duration_unit,
)


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
        nft = self.lending.nft()
        rent_duration_unit = get_rent_duration_unit(self.contract)

        if self.lending.daily_rent_price is not None:
            msg = (
                f"{nft.name} lent for "
                f"{self.lending.daily_rent_price} {self.lending.payment_token.name} "
                f"per day for a max of {self.lending.max_rent_duration} {rent_duration_unit} "
                f"by {self.lending.lender_address}. "
                f"{get_lending_url(self.contract, self.lending.lending_id)}"
            )
        else:
            msg = (
                f"{nft.name} lent for a fee of "
                f"{self.lending.upfront_rent_fee} {self.lending.payment_token.name} "
                f"for a max of {self.lending.max_rent_duration} {rent_duration_unit} "
                f"by {self.lending.lender_address}. "
                f"{get_lending_url(self.contract, self.lending.lending_id)}"
            )
        return msg

    def has_been_observed(self) -> bool:
        m = ReNFTModel.get_or_none(
            contract_name=self.contract.name,
            transaction_type=TransactionType.LEND,
        )

        return m is not None and self.lending.id <= attrgetter("renft_id")(m)

    def observe(self):
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
            name="Renter",
            value=f"{get_profile_url(self.contract, self.renting.renter_address)}",
            inline=False,
        )
        return msg

    def build_twitter_message(self):
        nft = self.renting.nft()
        rent_duration_unit = get_rent_duration_unit(self.contract)
        if self.renting.daily_rent_price is not None:
            msg = (
                f"{nft.name} rented for "
                f"{self.renting.daily_rent_price} {self.renting.payment_token.name} "
                f"per day for {self.renting.rent_duration} {rent_duration_unit} "
                f"by {self.renting.renter_address}. "
                f"{get_lending_url(self.contract, self.renting.lending_id)}"
            )
        else:
            msg = (
                f"{nft.name} rented for a fee of "
                f"{self.renting.upfront_rent_fee} {self.renting.payment_token.name} "
                f"for {self.renting.rent_duration} {rent_duration_unit} "
                f"by {self.renting.renter_address}. "
                f"{get_lending_url(self.contract, self.renting.lending_id)}"
            )
        return msg

    def has_been_observed(self) -> bool:
        m = ReNFTModel.get_or_none(
            contract_name=self.contract.name,
            transaction_type=TransactionType.RENT,
        )
        return m is not None and self.renting.id <= attrgetter("renft_id")(m)

    def observe(self):
        if not self.has_been_observed():
            ReNFTModel.update_or_create(
                contract_name=self.contract.name,
                transaction_type=TransactionType.RENT,
                defaults={"renft_id": self.renting.id},
            )
