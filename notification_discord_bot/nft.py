import json
from functools import cache

import requests

from notification_discord_bot.constants import NFT_PORT_API_KEY
from notification_discord_bot.logger import logger
from notification_discord_bot.renft import Chain, NonFungibleToken


@cache
def get_nft_with_nft_port(
    address: str, token_id: str, chain: Chain
) -> NonFungibleToken:
    chain_mapping = {chain.ETH: "ethereum", chain.MATIC: "polygon"}
    _chain = chain_mapping[chain]
    query_url = f"https://api.nftport.xyz/v0/nfts/{address}/{token_id}?chain=${_chain}"
    headers = {"content-type": "application/json", "Authorization": NFT_PORT_API_KEY}

    res = requests.get(query_url, headers=headers, timeout=20)
    res.raise_for_status()
    data = json.loads(res.content)
    return NonFungibleToken(
        name=data["metadata"]["name"],
        nft_address=data["contract_address"],
        token_id=data["token_id"],
        description=data["metadata"]["description"],
        image_url=data["cached_file_url"],
    )


@cache
def get_castle_crush_nft(address: str, token_id: str, chain: Chain) -> NonFungibleToken:
    if Chain.AVAX != chain:
        raise AssertionError("Invalid chain for Castle Crush.")
    hex_token_id = hex(int(token_id))[2:].rjust(64, "0")
    query_url = f"https://castle-crush-crypto-bucket.s3.amazonaws.com/metadata/{hex_token_id}.json"
    res = requests.get(query_url, timeout=20)
    res.raise_for_status()
    data = json.loads(res.content)
    return NonFungibleToken(
        name=data["name"],
        nft_address=address,
        token_id=token_id,
        image_url=data["image"],
        description=data["description"],
    )


def get_placeholder_nft(address: str, token_id: str, chain: Chain):
    logger.warning(f"Using placeholder NFT for {address}#{token_id} on {str(chain)}.")
    return NonFungibleToken(
        name=address,
        nft_address=address,
        token_id=token_id,
        image_url="https://v2.renft.io/assets/placeholder.png",
        description="",
    )


def get_nft(address: str, token_id: str, chain: Chain) -> NonFungibleToken:
    try:
        if chain in {Chain.ETH, Chain.MATIC}:
            return get_nft_with_nft_port(address, token_id, chain)
        if chain in {Chain.AVAX}:
            return get_castle_crush_nft(address, token_id, chain)
    except:
        pass
    return get_placeholder_nft(address, token_id, chain)
