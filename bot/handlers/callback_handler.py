"""../bot/handlers/callback_handler.py"""

from functools import partial
from typing import Type

from telethon import events

from bot.conversation_flow import ConversationFlow
from bot.services.dynamodb_crud_manager import DynamoDBCrudManager


def initialize_callback_handler(
    conversation_flow: Type[ConversationFlow],
    dynamodb_crud_manager: DynamoDBCrudManager,
) -> partial:
    """Initializes the callback handler."""
    handler = partial(
        handle_callback_query,
        conversation_flow=conversation_flow,
        dynamodb_crud_manager=dynamodb_crud_manager,
    )
    return events.register(events.CallbackQuery())(handler)


async def handle_callback_query(
    event: events.CallbackQuery.Event,
    dynamodb_crud_manager: DynamoDBCrudManager,
    conversation_flow: Type[ConversationFlow],
):
    """Handles callback query."""
    user_id = str(event.sender_id)

    async with conversation_flow(
        user_id=user_id,
        dynamodb_crud_manager=dynamodb_crud_manager,
        telethon_event=event,
    ) as conversation:
        callback_data = event.data.decode("utf-8")
        await conversation.trigger_callback(callback_data)
