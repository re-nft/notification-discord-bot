from operator import attrgetter

import discord

from notification_discord_bot.constants import TwitterMessage
from notification_discord_bot.models import ReNFTModel
from notification_discord_bot.renft import (
    Lending,
    ReNFTContract,
    ReNFTDatum,
    Renting,
    TransactionType,
    calculate_reward_share,
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
        profile_url = get_profile_url(self.contract, self.lending.lender_address)

        msg = discord.Embed(
            title=f"{nft.name} Lent",
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
        if self.lending.revshare_beneficiaries and self.lending.revshare_portions:
            reward_share = calculate_reward_share(
                self.lending.lender_address,
                self.lending.revshare_beneficiaries,
                self.lending.revshare_portions,
            )
            msg.add_field(
                name="Reward Split",
                value=(
                    f"{reward_share.lender}% L / "
                    f"{reward_share.other}% O / "
                    f"{reward_share.renter}% R"
                ),
                inline=True,
            )
        msg.add_field(
            name="Lender",
            value=f"[{self.lending.lender_address}]({profile_url})",
            inline=False,
        )
        return msg

    def build_twitter_message(self):
        nft = self.lending.nft()
        rent_duration_unit = get_rent_duration_unit(self.contract)

        if self.lending.daily_rent_price is not None:
            lent_price = self.lending.daily_rent_price
        else:
            lent_price = f"a fee of {self.lending.upfront_rent_fee}"

        reward_split = ""
        if self.lending.revshare_beneficiaries and self.lending.revshare_portions:
            reward_share = calculate_reward_share(
                self.lending.lender_address,
                self.lending.revshare_beneficiaries,
                self.lending.revshare_portions,
            )
            reward_split = (
                f"The reward split is {reward_share.lender}% to the lender, "
                f"{reward_share.renter}% to the renter, "
                f"and {reward_share.other} to others."
            )

        msg = (
            f"{nft.name} lent for {lent_price} {self.lending.payment_token.name} "
            f"for a max of {self.lending.max_rent_duration} {rent_duration_unit} "
            f"by {self.lending.lender_address}. "
            f"{reward_split} "
            f"{get_lending_url(self.contract, self.lending.lending_id)}"
        )
        return TwitterMessage(msg, nft.image_url)

    def has_been_observed(self) -> bool:
        m = ReNFTModel.get_or_none(
            contract_name=self.contract.name,
            transaction_type=TransactionType.LEND,
        )

        return m is not None and self.lending.cursor <= attrgetter("renft_id")(m)

    def observe(self):
        if not self.has_been_observed():
            ReNFTModel.update_or_create(
                contract_name=self.contract.name,
                transaction_type=TransactionType.LEND,
                defaults={"renft_id": self.lending.cursor},
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
        profile_url = get_profile_url(self.contract, self.renting.renter_address)

        msg = discord.Embed(
            title=f"{nft.name} Rented",
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
        if self.renting.revshare_beneficiaries and self.renting.revshare_portions:
            reward_share = calculate_reward_share(
                self.renting.lender_address,
                self.renting.revshare_beneficiaries,
                self.renting.revshare_portions,
            )
            msg.add_field(
                name="Reward Split",
                value=(
                    f"{reward_share.lender}% L / "
                    f"{reward_share.other}% O / "
                    f"{reward_share.renter}% R"
                ),
                inline=True,
            )
        msg.add_field(
            name="Renter",
            value=f"[{self.renting.renter_address}]({profile_url})",
            inline=False,
        )

        return msg

    def build_twitter_message(self):
        nft = self.renting.nft()
        rent_duration_unit = get_rent_duration_unit(self.contract)
        if self.renting.daily_rent_price is not None:
            rent_price = self.renting.daily_rent_price
        else:
            rent_price = f"a fee of {self.renting.upfront_rent_fee}"

        reward_split = ""
        if self.renting.revshare_beneficiaries and self.renting.revshare_portions:
            reward_share = calculate_reward_share(
                self.renting.lender_address,
                self.renting.revshare_beneficiaries,
                self.renting.revshare_portions,
            )
            reward_split = (
                f"The reward split is {reward_share.lender}% to the lender, "
                f"{reward_share.renter}% to the renter, "
                f"and {reward_share.other} to others."
            )
        msg = (
            f"{nft.name} rented for {rent_price} {self.renting.payment_token.name} "
            f"for {self.renting.rent_duration} {rent_duration_unit} "
            f"by {self.renting.renter_address}. "
            f"{reward_split} "
            f"{get_lending_url(self.contract, self.renting.lending_id)}"
        )
        return TwitterMessage(msg, nft.image_url)

    def has_been_observed(self) -> bool:
        m = ReNFTModel.get_or_none(
            contract_name=self.contract.name,
            transaction_type=TransactionType.RENT,
        )
        return m is not None and self.renting.cursor <= attrgetter("renft_id")(m)

    def observe(self):
        if not self.has_been_observed():
            ReNFTModel.update_or_create(
                contract_name=self.contract.name,
                transaction_type=TransactionType.RENT,
                defaults={"renft_id": self.renting.cursor},
            )
