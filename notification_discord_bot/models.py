from dataclasses import dataclass

from notification_discord_bot.db import Model
from notification_discord_bot.renft import TransactionType


@dataclass
class ReNFTModel(Model):
    contract_name: str
    transaction_type: TransactionType
    renft_id: str

    @classmethod
    def collection_name(cls):
        return "renft"

    @classmethod
    def unique_index(cls):
        return {"contract_name", "transaction_type"}
