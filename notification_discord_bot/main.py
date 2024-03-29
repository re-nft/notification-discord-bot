#!/usr/bin/env python

import os
import time
from dataclasses import asdict
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

import discord
import requests
import tweepy

from notification_discord_bot import constants, utils
from notification_discord_bot.contracts import all_contracts, contract_is_enabled
from notification_discord_bot.logger import logger
from notification_discord_bot.seed import seed


class MessageSender:
    def __init__(self):
        if utils.discord_enabled():
            self.discord_webhook = discord.Webhook.from_url(
                constants.DISCORD_WEBHOOK, adapter=discord.RequestsWebhookAdapter()
            )
        if utils.twitter_enabled():
            self.authenticate_twitter()

    def authenticate_twitter(self):
        auth = tweepy.OAuthHandler(
            constants.TWEEPY_API_KEY,
            constants.TWEEPY_API_SECRET,
            constants.TWEEPY_ACCESS_TOKEN,
            constants.TWEEPY_ACCESS_TOKEN_SECRET,
        )
        self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
        self.twitter_api.verify_credentials()

    def send_discord_message(self, msg):
        logger.debug(msg.to_dict())
        if utils.discord_enabled():
            try:
                self.discord_webhook.send(embed=msg)
            except discord.HTTPException as e:
                if e.response.status == 429:
                    retry_after = float(e.response.headers["Retry-After"])
                    logger.info(f"Retrying after {str(retry_after)}s")
                    time.sleep(retry_after)
                    self.discord_webhook.send(embed=msg)
                else:
                    raise e

    def send_twitter_message(self, msg: constants.TwitterMessage):
        logger.debug(asdict(msg))
        if utils.twitter_enabled():
            media_ids = []
            try:
                res = requests.get(msg.image_url, timeout=20)
                res.raise_for_status()
                a = urlparse(msg.image_url)
                filename = os.path.basename(a.path)
                with NamedTemporaryFile(suffix=filename) as t:
                    t.write(res.content)
                    media = self.twitter_api.media_upload(t.name)
                    if media:
                        media_ids = [media.media_key.split("_")[1]]
            except:
                logger.exception(f"Cannot get image {msg.image_url}")
            try:
                self.twitter_api.update_status(status=msg.message, media_ids=media_ids)
            except tweepy.Forbidden:
                logger.exception("Tweepy 403")


def check_for_updates(msg_sender: MessageSender):
    for contract in all_contracts:
        if contract_is_enabled(contract):
            # Reversed because the order is originally descending,
            # but we want observe in ascending order
            for renft_datum in [
                *reversed(contract.get_lendings()),
                *reversed(contract.get_rentings()),
            ]:
                if renft_datum.has_been_observed():
                    continue
                renft_datum.observe()

                discord_message = renft_datum.build_discord_message()
                msg_sender.send_discord_message(discord_message)

                twitter_message = renft_datum.build_twitter_message()
                msg_sender.send_twitter_message(twitter_message)
                time.sleep(constants.RATE_LIMIT_SLEEP_TIME_S)


def main():
    logger.info(f"Discord is enabled: {utils.discord_enabled()}")
    logger.info(f"Twitter is enabled: {utils.twitter_enabled()}")
    seed()
    msg_sender = MessageSender()
    while True:
        check_for_updates(msg_sender)
        logger.info(f"Sleeping for {str(constants.SLEEP_TIME_S)} seconds.")
        time.sleep(constants.SLEEP_TIME_S)


if __name__ == "__main__":
    main()
