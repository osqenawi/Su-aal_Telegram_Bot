"""../bot/bot.py"""

import logging
from typing import Callable

from clients.telethon_client import TelethonClient


class TelegramBot:
    """A class representing the main Telegram bot."""

    def __init__(
        self,
        bot_client: TelethonClient,
        user_client: TelethonClient,
        handlers: list[Callable],
        logger=None,
    ):
        self.bot_client = bot_client
        self.user_client = user_client
        self.handlers = handlers
        self.logger = logger or logging.getLogger(__name__)

    async def connect_to_telegram(self):
        """Connects to the Telegram server by starting the user and bot clients."""
        async with self.user_client, self.bot_client:
            self.logger.info("Bot started!")
            await self.bot_client.telethon_client.run_until_disconnected()

    def register_handlers(
        self,
    ):
        """Registers event handlers for the bot."""
        for handler in self.handlers:
            self.bot_client.telethon_client.add_event_handler(handler)

    async def start(self):
        """Starts the bot."""
        self.register_handlers()
        await self.connect_to_telegram()

    async def cleanup(self):
        """Cleans up resources when the bot is done."""
        await self.user_client.cleanup()
        await self.bot_client.cleanup()
        self.logger.info("Bot cleanup completed.")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.cleanup()
