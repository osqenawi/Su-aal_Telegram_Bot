"""
../scripts/auth_script.py
Script for user and bot authorization.
"""

import asyncio

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError, PhoneNumberInvalidError

from config.file_path_config import FilePathConfig
from config.telegram_config import TelegramConfig


class ClientAuthenticator:
    """
    Authenticator class for user and bot authorization.
    """

    def __init__(self, client: TelegramClient, bot_token: str = ""):
        self.client = client
        self.bot_token = bot_token
        self.is_bot = bool(bot_token)

    async def authenticate(self):
        """Authenticate the client (either user or bot)."""
        client_type = "bot" if self.is_bot else "user account"
        print(f"Authenticating {client_type}...")

        try:
            await self._start_client()
            print(f"{client_type.capitalize()} authentication complete.")
        except SessionPasswordNeededError as e:
            print(
                f"Authentication failed: {e}. Please check your credentials and try again."
            )
        except (PhoneCodeInvalidError, PhoneNumberInvalidError) as e:
            print(
                f"Authentication failed: {e}. Please verify your phone number and try again."
            )

    async def _start_client(self):
        """Determine the client type and start the client."""
        if self.is_bot:
            await self.client.start(bot_token=self.bot_token)
        else:
            await self._start_user_client()

    async def _start_user_client(self):
        """Start the user client."""
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self._request_phone_authentication()

    async def _request_phone_authentication(self):
        """Request phone number authentication for the user client."""
        phone_number = input("Enter your phone number with the country code: ")
        await self.client.send_code_request(phone_number)
        code = input("Enter the code you received: ")
        try:
            await self.client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = input(
                "Two-step verification enabled. Please enter your password: "
            )
            await self.client.sign_in(password=password)


async def authenticate_clients(
    user_session_file: str,
    bot_session_file: str,
    api_id: int,
    api_hash: str,
    bot_token: str,
):
    """Authenticate both bot and user clients concurrently."""
    user_client = TelegramClient(user_session_file, api_id, api_hash)
    bot_client = TelegramClient(bot_session_file, api_id, api_hash)

    bot_authenticator = ClientAuthenticator(bot_client, bot_token)
    user_authenticator = ClientAuthenticator(user_client)

    await asyncio.gather(
        bot_authenticator.authenticate(), user_authenticator.authenticate()
    )


if __name__ == "__main__":
    asyncio.run(
        authenticate_clients(
            user_session_file=FilePathConfig.TELETHON_USER_SESSION_FILE,
            bot_session_file=FilePathConfig.TELETHON_BOT_SESSION_FILE,
            api_id=int(TelegramConfig.API_ID),
            api_hash=TelegramConfig.API_HASH,
            bot_token=TelegramConfig.BOT_TOKEN,
        )
    )
