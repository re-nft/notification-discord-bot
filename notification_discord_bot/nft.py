import json
from dataclasses import dataclass
from functools import cache
from typing import Any

import requests

from notification_discord_bot.constants import (
    ETHEREUM_ALCHEMY_BASE_URL,
    NFT_PORT_API_KEY,
    POLYGON_ALCHEMY_BASE_URL,
)
from notification_discord_bot.logger import logger
from notification_discord_bot.renft import Chain, NonFungibleToken
from notification_discord_bot.utils import normalize_ipfs_url


@dataclass
class RankedUrl:
    rank: int
    url: str


def get_ranked_url(url: str, min_rank: int = 0) -> RankedUrl:
    if "alchemyapi" in url:
        return RankedUrl(4, url)
    if url.startswith("ipfs"):
        return RankedUrl(1, url)
    if "ipfs" in url:
        return RankedUrl(3, url)
    return RankedUrl(min_rank, url)


def get_image_url_from_alchemy_nft(nft: dict[str, Any]):
    media_urls: list[RankedUrl] = []

    if metadata_image := nft["metadata"].get("image"):
        media_urls.append(get_ranked_url(metadata_image, 3))

    if metadata_image_url := nft["metadata"].get("image_url"):
        media_urls.append(get_ranked_url(metadata_image_url, 3))

    if media := nft.get("media"):
        for medium in media:
            if medium_gateway := medium.get("gateway"):
                media_urls.append(get_ranked_url(medium_gateway, 2))
            if medium_raw := medium.get("raw"):
                media_urls.append(get_ranked_url(medium_raw))

    media_urls = [u for u in media_urls if u.url != ""]
    media_urls.sort(key=lambda n: n.rank, reverse=True)
    if len(media_urls) == 0:
        raise ValueError(
            f"No image url found for NFT {nft['contract']['address']}#{nft['id']['tokenId']}."
        )
    return media_urls[0].url


@cache
def get_nft_with_alchemy(address: str, token_id: str, chain: Chain) -> NonFungibleToken:
    base_url_mapping = {
        chain.ETH: f"{ETHEREUM_ALCHEMY_BASE_URL}/getNFTMetadata",
        chain.MATIC: f"{POLYGON_ALCHEMY_BASE_URL}/getNFTMetadata",
    }
    base_url = base_url_mapping[chain]
    query_params = f"?contractAddress={address}&tokenId={token_id}"
    query_url = base_url + query_params
    headers = {"accept": "application/json"}

    res = requests.get(query_url, headers=headers, timeout=20)
    res.raise_for_status()
    data = json.loads(res.content)
    return NonFungibleToken(
        name=data["metadata"]["name"],
        nft_address=data["contract"]["address"],
        token_id=data["id"]["tokenId"],
        description=data["metadata"]["description"],
        image_url=normalize_ipfs_url(get_image_url_from_alchemy_nft(data)),
    )


@cache
def get_nft_with_nft_port(
    address: str, token_id: str, chain: Chain
) -> NonFungibleToken:
    if not NFT_PORT_API_KEY:
        raise ValueError("NFTPort API key not set.")
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
            try:
                return get_nft_with_alchemy(address, token_id, chain)
            except:
                return get_nft_with_nft_port(address, token_id, chain)
        if chain in {Chain.AVAX}:
            return get_castle_crush_nft(address, token_id, chain)
    except:
        pass
    return get_placeholder_nft(address, token_id, chain)
