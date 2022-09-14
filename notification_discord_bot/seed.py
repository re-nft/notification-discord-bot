from notification_discord_bot.contracts import all_contracts
from notification_discord_bot.logger import logger
from notification_discord_bot.models import ReNFTModel


def contract_is_seeded(contract_name: str) -> bool:
    return len(ReNFTModel.filter(contract_name=contract_name)) != 0


def seed_renft():
    for contract in all_contracts:
        if contract_is_seeded(contract.name):
            continue

        logger.info(f"Seeding lendings for {contract.name}")
        lendings = contract.get_lendings()
        for lending in lendings:
            lending.observe()

        logger.info(f"Seeding rentings for {contract.name}")
        rentings = contract.get_rentings()
        for renting in rentings:
            renting.observe()
