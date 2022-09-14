import json
from typing import Any
import requests
from notification_discord_bot import constants
from notification_discord_bot.contracts import ReNFTContract
from notification_discord_bot.logger import logger


def twitter_enabled() -> bool:
    return all(
        c is not None
        for c in [
            constants.TWEEPY_API_KEY,
            constants.TWEEPY_API_SECRET,
            constants.TWEEPY_ACCESS_TOKEN,
            constants.TWEEPY_ACCESS_TOKEN_SECRET,
        ]
    )


def discord_enabled() -> bool:
    return constants.DISCORD_WEBHOOK is not None


def get_rent_duration_unit(contract: ReNFTContract) -> str:
    from notification_discord_bot.contracts import AvalancheWhoopiContract

    return "cycles" if isinstance(contract, AvalancheWhoopiContract) else "days"


def get_profile_url(contract: ReNFTContract, address: str):
    from notification_discord_bot.renft import Chain

    chain = contract.chain()
    chain_mapping = {
        Chain.ETH: f"https://etherscan.io/address/{address}",
        Chain.MATIC: f"https://polygonscan.com/address/{address}",
        Chain.AVAX: f"https://snowtrace.io/address/{address}",
    }
    return chain_mapping[chain]


def get_lending_url(contract: ReNFTContract, lending_id: str):
    from notification_discord_bot.renft import Chain

    from notification_discord_bot.contracts import AvalancheWhoopiContract

    if isinstance(contract, AvalancheWhoopiContract):
        return f"{constants.RENFT_BASE_URL}/collections/castle-crush?lendingId={lending_id}"
    contract_type = "collateral_free" if contract.is_collateral_free() else "collateral"
    return f"{constants.RENFT_BASE_URL}?ctx={contract_type}&lendingId={lending_id}"


def construct_the_graph_query(query: str, first: int, skip: int) -> str:
    query = query.replace("$first", str(first))
    query = query.replace("$skip", str(skip))
    return query


def query_the_graph(
    query_url: str, query: str, first=constants.DEFAULT_PAGE_SIZE, skip=0
):
    the_graph_query = construct_the_graph_query(query, first, skip)
    res = requests.post(query_url, json={"query": the_graph_query})
    res.raise_for_status()
    data = json.loads(res.content)
    if errors := data.get("errors"):
        logger.error(f"Error in {query_url} with query:\n{the_graph_query}")
        raise RuntimeError(str(errors))
    return data
