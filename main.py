"""./main.py"""

import asyncio
from typing import Type

from bot.bot import TelegramBot

from bot.conversation_flow import ConversationFlow

from bot.handlers.callback_handler import initialize_callback_handler
from bot.handlers.message_handlers import initialize_text_messege_handler
from bot.handlers.start_handler import initialize_start_handler

from bot.services.dynamodb_crud_manager import DynamoDBCrudManager
from clients.dynamodb_client import DynamoDBClient
from clients.telethon_client import TelethonClient

from config.dynamodb_config import DynamoDBConfig
from config.file_path_config import FilePathConfig
from config.logging.config_logging import setup_logging
from config.state_machine.state_machine_config import create_state_machine_config
from config.telegram_config import TelegramConfig


async def run_bot(
    bot_client_param: TelethonClient,
    user_client_param: TelethonClient,
    dynamodb_client: DynamoDBClient,
    dynamodb_crud_manager: DynamoDBCrudManager,
    logging_config_file: str,
    conversation_flow: Type[ConversationFlow],
) -> None:
    """Run the Telegram bot."""
    setup_logging(logging_config_file)

    async with dynamodb_client as dynamodb_client:
        await _run_bot(
            bot_client_param=bot_client_param,
            user_client_param=user_client_param,
            dynamodb_crud_manager=dynamodb_crud_manager,
            conversation_flow=conversation_flow,
        )


async def _run_bot(
    bot_client_param: TelethonClient,
    user_client_param: TelethonClient,
    dynamodb_crud_manager: DynamoDBCrudManager,
    conversation_flow: Type[ConversationFlow],
) -> None:
    handlers = [
        initialize_start_handler(conversation_flow, dynamodb_crud_manager),
        initialize_callback_handler(conversation_flow, dynamodb_crud_manager),
        initialize_text_messege_handler(conversation_flow, dynamodb_crud_manager),
    ]
    async with TelegramBot(
        bot_client=bot_client_param, user_client=user_client_param, handlers=handlers
    ):
        pass


if __name__ == "__main__":
    bot_client = TelethonClient(
        session_file=FilePathConfig.TELETHON_BOT_SESSION_FILE,
        api_id=int(TelegramConfig.API_ID),
        api_hash=TelegramConfig.API_HASH,
    )
    user_client = TelethonClient(
        session_file=FilePathConfig.TELETHON_USER_SESSION_FILE,
        api_id=int(TelegramConfig.API_ID),
        api_hash=TelegramConfig.API_HASH,
    )
    db_client = DynamoDBClient(
        region_name=DynamoDBConfig.AWS_REGION_NAME,
    )
    db_crud_manager = DynamoDBCrudManager(
        dynamodb_client=db_client, table_name=DynamoDBConfig.TABLE_NAME
    )

    state_machine_config = create_state_machine_config()
    ConversationFlow.config(config=state_machine_config)

    asyncio.run(
        run_bot(
            bot_client_param=bot_client,
            user_client_param=user_client,
            logging_config_file=FilePathConfig.LOGGING_CONFIG_FILE,
            dynamodb_client=db_client,
            dynamodb_crud_manager=db_crud_manager,
            conversation_flow=ConversationFlow,
        )
    )
