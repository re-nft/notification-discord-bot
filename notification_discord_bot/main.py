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
from notification_discord_bot.contracts import all_contracts
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
            self.discord_webhook.send(embed=msg)

    def send_twitter_message(self, msg: constants.TwitterMessage):
        logger.debug(asdict(msg))
        if utils.twitter_enabled():
            try:
                res = requests.get(msg.image_url, timeout=20)
                res.raise_for_status()
                a = urlparse(msg.image_url)
                filename = os.path.basename(a.path)
                with NamedTemporaryFile(suffix=filename) as t:
                    t.write(res.content)
                    media = self.twitter_api.media_upload(t.name)
                    media_ids = [media.media_ids]
            except:
                logger.exception(f"Cannot get image {msg.image_url}")
                media_ids = []
            try:
                self.twitter_api.update_status(status=msg.message, media_ids=media_ids)
            except tweepy.errors.Forbidden:
                logger.exception("Tweepy 403")


def check_for_updates(msg_sender: MessageSender):
    for contract in all_contracts:
        for renft_datum in [*contract.get_lendings(), *contract.get_rentings()]:
            if renft_datum.has_been_observed():
                continue
            renft_datum.observe()

            discord_message = renft_datum.build_discord_message()
            msg_sender.send_discord_message(discord_message)

            twitter_message = renft_datum.build_twitter_message()
            msg_sender.send_twitter_message(twitter_message)


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
