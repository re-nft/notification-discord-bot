import json

import requests

from notification_discord_bot import constants
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


def construct_the_graph_query(query: str, first: int, skip: int) -> str:
    query = query.replace("$first", str(first))
    query = query.replace("$skip", str(skip))
    return query


def query_the_graph(
    query_url: str, query: str, first=constants.DEFAULT_PAGE_SIZE, skip=0
):
    the_graph_query = construct_the_graph_query(query, first, skip)
    res = requests.post(query_url, json={"query": the_graph_query}, timeout=20)
    res.raise_for_status()
    data = json.loads(res.content)
    if errors := data.get("errors"):
        logger.error(f"Error in {query_url} with query:\n{the_graph_query}")
        raise RuntimeError(str(errors))
    return data


def normalize_ipfs_url(url: str) -> str:
    if not url.startswith("ipfs://"):
        return url
    suffix = url.partition("ipfs://")[2]
    return f"{constants.IPFS_GATEWAY_URL}/{suffix}"
