#!/usr/bin/env python

import time

import discord
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

    def send_twitter_message(self, msg):
        logger.debug(msg)
        if utils.twitter_enabled():
            try:
                self.twitter_api.update_status(msg)
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
