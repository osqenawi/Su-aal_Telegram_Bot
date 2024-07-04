"""../clients/user_client.py"""

import logging
from telethon import TelegramClient


class TelethonClient:
    """User Account Client for interacting with the Telegram API."""

    def __init__(self, session_file: str, api_id: int, api_hash: str, logger=None):
        """Initialize the UserClient."""
        self.telethon_client = TelegramClient(
            session_file,
            api_id,
            api_hash,
            request_retries=-1, # Infinite retries
            flood_sleep_threshold=7 * 24 * 60 * 60, # 1 week
        )
        self.logger = logger or logging.getLogger(__name__)

    async def connect(self):
        """Connect to the Telegram API."""
        await self.telethon_client.connect()

        if not await self.telethon_client.is_user_authorized():
            self.logger.warning("Client not authorized. Run the auth script.")
            return

        self.logger.info("Client started!")

    async def setup(self):
        """Perform setup tasks for the client."""
        await self.connect()

    async def cleanup(self):
        """Clean up resources when the client is done."""
        await self.telethon_client.disconnect()

    async def __aenter__(self):
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.cleanup()
