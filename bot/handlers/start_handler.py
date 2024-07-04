"""../bot/handlers/start_handler.py"""

from typing import Type
from functools import partial

from telethon import events

from bot.conversation_flow import ConversationFlow
from bot.services.dynamodb_crud_manager import DynamoDBCrudManager


def initialize_start_handler(
    conversation_flow: Type[ConversationFlow],
    dynamodb_crud_manager: DynamoDBCrudManager,
) -> partial:
    """Initializes the start handler."""
    handler = partial(
        handle_start_command,
        conversation_flow=conversation_flow,
        dynamodb_crud_manager=dynamodb_crud_manager,
    )
    return events.register(events.NewMessage(pattern="/start"))(handler)


async def handle_start_command(
    event: events.NewMessage.Event,
    dynamodb_crud_manager: DynamoDBCrudManager,
    conversation_flow: Type[ConversationFlow],
):
    """Handles the /start command event. Sends a welcome message to the chat."""
    if not event.is_private:
        return

    user_id = str(event.sender.id)

    async with conversation_flow(
        user_id=user_id,
        dynamodb_crud_manager=dynamodb_crud_manager,
        telethon_event=event,
    ) as conversation:
        await conversation.trigger_start()

    raise events.StopPropagation
