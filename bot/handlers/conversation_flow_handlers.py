"""../bot/handlers/conversation_flow_handlers.py"""

from typing import Any, Dict, List, Tuple

import ulid
from telethon import TelegramClient
from telethon.events import CallbackQuery, NewMessage
from telethon.tl.custom import Button
from telethon.tl.custom.message import Message
from telethon.tl.types import KeyboardButtonCallback
from transitions.extensions.asyncio import AsyncEventData

from bot.services.dynamodb_constants import (
    DynamoDBAttributes,
    DynamoDBFormatter,
    DynamoDBGSI1QuestionStatusValues,
    DynamoDBKeySchema,
)
from bot.services.dynamodb_crud_manager import DynamoDBCrudManager
from config.state_machine.state_machine_config import StateMachineConfig

StateInlineButtonsData = list[str | list[str]]
InlineButtons = List[KeyboardButtonCallback]


class DynamoDBMixin:
    """Mixin class to handle DynamoDB operations."""

    def __init__(self, dynamodb_crud_manager: DynamoDBCrudManager, user_id: str):
        self.dynamodb_crud_manager = dynamodb_crud_manager
        self.dynamodb_user_pk = DynamoDBFormatter.prefix_user_pk(user_id)
        self.dynamodb_user_sk = DynamoDBFormatter.prefix_user_sk(user_id)

    async def update_user_state_in_db(self, state: str):
        """Updates the user's state in the database."""
        await self.dynamodb_crud_manager.update_attributes(
            pk=self.dynamodb_user_pk,
            sk=self.dynamodb_user_sk,
            attributes={DynamoDBAttributes.USER_STATE.value: state},
        )

    async def store_user_input_in_db(self, state: str, user_input: str):
        """Stores the user's input in the database."""
        user_inputs = await self.get_user_inputs_from_db()
        user_inputs[state] = user_input
        await self.dynamodb_crud_manager.update_attributes(
            pk=self.dynamodb_user_pk,
            sk=self.dynamodb_user_sk,
            attributes={DynamoDBAttributes.USER_INPUTS.value: user_inputs},
        )

    async def get_user_inputs_from_db(self) -> Dict[str, str]:
        """Retrieves the user's inputs from the database."""
        response = await self.dynamodb_crud_manager.get_attribute(
            attribute=DynamoDBAttributes.USER_INPUTS.value,
            pk=self.dynamodb_user_pk,
            sk=self.dynamodb_user_sk,
        )
        return response if isinstance(response, dict) else {}

    async def get_destination_chat(self) -> str:
        """Gets the destination chat for the user."""
        response = await self.dynamodb_crud_manager.get_attribute(
            attribute=DynamoDBAttributes.DESTINATION_CHAT.value,
            pk=self.dynamodb_user_pk,
            sk=self.dynamodb_user_sk,
        )
        return response if isinstance(response, str) else ""

    async def get_destination_chat_topic(self) -> str:
        """Gets the destination chat topic for the user."""
        response = await self.dynamodb_crud_manager.get_attribute(
            attribute=DynamoDBAttributes.DESTINATION_CHAT_TOPIC.value,
            pk=self.dynamodb_user_pk,
            sk=self.dynamodb_user_sk,
        )
        return response if isinstance(response, str) else ""

    async def store_destination_chat(self, chat_id):
        """Stores the destination chat for the user."""
        await self.dynamodb_crud_manager.update_attributes(
            pk=self.dynamodb_user_pk,
            sk=self.dynamodb_user_sk,
            attributes={DynamoDBAttributes.DESTINATION_CHAT.value: chat_id},
        )

    async def store_destination_chat_topic(self, topic_id):
        """Stores the destination chat topic for the user."""
        await self.dynamodb_crud_manager.update_attributes(
            pk=self.dynamodb_user_pk,
            sk=self.dynamodb_user_sk,
            attributes={DynamoDBAttributes.DESTINATION_CHAT_TOPIC.value: topic_id},
        )


class StateHandler:
    """Class to handle state-related operations."""

    def __init__(self, config: StateMachineConfig):
        self.config = config

    def get_state_message(self, state: str) -> str:
        """Extracts the message for the given state."""
        return self.config.messages.get(state, "")

    def get_state_inline_buttons(self, state: str) -> StateInlineButtonsData:
        """Extracts the inline buttons for the given state."""
        return self.config.inline_buttons.get(state, [""])

    def get_state_destination_chat(self, state: str) -> str:
        """Gets the destination chat for the given state."""
        return self.config.destinations.get(state, {}).get("chat_id", "")

    def get_state_destination_chat_topic(self, state: str) -> str:
        """Gets the destination chat topic for the given state."""
        return self.config.destinations.get(state, {}).get("topic_id", "")


class QuestionHandler:
    """A Class to handle question-related operations."""

    def __init__(
        self,
        dynamodb_crud_manager: DynamoDBCrudManager,
        telethon_event: NewMessage.Event | CallbackQuery.Event,
        user_id: str,
        dynamodb_mixin: DynamoDBMixin,
        state_handler: StateHandler,
    ):
        self.dynamodb_crud_manager = dynamodb_crud_manager
        self.telethon_event = telethon_event
        self.user_id = user_id
        self.dynamodb_mixin = dynamodb_mixin
        self.state_handler = state_handler
        self.telethon_client: TelegramClient = telethon_event.client

    async def process_question_submission(
        self, event: AsyncEventData
    ):  # pylint: disable=unused-argument
        """Processes the user's question submission."""
        question_item = await self._new_question_in_db()
        destination_chat, destination_chat_topic = await self._get_destination()
        question_message_id = await self._send_formatted_question(
            question_item, destination_chat, destination_chat_topic
        )
        await self._add_question_message_id_to_db(
            question_sk=question_item[DynamoDBKeySchema.SK.value],
            dest_question_message_id=question_message_id,
            dest_chat_id=destination_chat,
        )

    async def _send_formatted_question(
        self,
        question_item: Dict[str, Any],
        destination_chat: str,
        destination_chat_topic: str,
    ) -> int:
        """Formats and sends the question message, returning the message ID."""
        question_message = self._format_question_message(question_item)
        return await self._send_question_to_destination(
            question_message=question_message,
            destination_chat=destination_chat,
            destination_chat_topic=destination_chat_topic,
        )

    async def _new_question_in_db(self) -> Dict[str, Any]:
        """Creates a new question in the database."""
        question_data = self._build_question_data(
            message=self.telethon_event.message,  # type: ignore
            user_inputs=await self.dynamodb_mixin.get_user_inputs_from_db(),
        )
        question_item = self._prepare_question_item(data=question_data)
        await self._store_question(question_item=question_item)
        return question_item

    def _extract_message_info(self) -> tuple[int, int, str, str, str]:
        """Extracts message information."""
        message = self.telethon_event.message  # type: ignore
        return (
            message.id,
            message.sender_id,
            message.sender.username,
            message.sender.first_name,
            message.sender.last_name,
        )

    @staticmethod
    def _build_question_data(
        message: Message, user_inputs: dict[str, str]
    ) -> dict[str, Any]:
        """Builds the question data dictionary."""
        return {
            DynamoDBAttributes.QUESTION_ID.value: message.id,
            DynamoDBAttributes.USER_ID.value: message.sender_id,
            DynamoDBAttributes.USER_USERNAME.value: (
                f"@{message.sender.username}" if message.sender.username else "لا يوجد"  # type: ignore
            ),
            DynamoDBAttributes.USER_FIRST_NAME.value: message.sender.first_name,  # type: ignore
            DynamoDBAttributes.USER_LAST_NAME.value: message.sender.last_name,  # type: ignore
            DynamoDBAttributes.USER_FULL_NAME.value: f"{message.sender.first_name} {message.sender.last_name or ''}",  # type: ignore
            DynamoDBAttributes.QUESTION_STATUS.value: DynamoDBGSI1QuestionStatusValues.NON_ANSWERED.value,
            **user_inputs,
        }

    def _generate_ulid(self) -> str:
        """Generates ULID for question SK."""
        question_id = str(ulid.new())
        return DynamoDBFormatter.prefix_question_sk(question_id=question_id)

    def _prepare_question_item(self, data: dict) -> dict:
        """Prepares the question item for storage in DynamoDB."""
        return {
            DynamoDBKeySchema.PK.value: self.dynamodb_mixin.dynamodb_user_pk,
            DynamoDBKeySchema.SK.value: self._generate_ulid(),
            DynamoDBKeySchema.GSI1_PK.value: DynamoDBFormatter.prefix_question_status_gsi1_pk(
                DynamoDBGSI1QuestionStatusValues.NON_ANSWERED.value
            ),
            DynamoDBKeySchema.GSI1_SK.value: self.dynamodb_mixin.dynamodb_user_pk,
            **data,
        }

    async def _store_question(self, question_item):
        """Stores the question item in DynamoDB."""
        await self.dynamodb_crud_manager.put_item(item=question_item)

    async def _add_question_message_id_to_db(
        self, question_sk: str, dest_question_message_id: int, dest_chat_id: str
    ):
        """Adds the destination question message ID to the user's item in the database."""
        dest_chat_gsi2_pk = self._get_dest_chat_gsi2_pk(dest_chat_id=dest_chat_id)
        dest_message_gsi2_pk = self._get_dest_message_gsi2_sk(
            dest_message_id=str(dest_question_message_id)
        )
        await self._add_dest_message_gsi2_sk_to_question_item(
            question_sk=question_sk,
            dest_chat_gsi2_pk=dest_chat_gsi2_pk,
            dest_message_gsi2_sk=dest_message_gsi2_pk,
        )

    async def _add_dest_message_gsi2_sk_to_question_item(
        self, question_sk: str, dest_chat_gsi2_pk: str, dest_message_gsi2_sk: str
    ):
        """Adds the destination message GSI2 PK to the question item in the database."""
        await self.dynamodb_crud_manager.update_attributes(
            pk=self.dynamodb_mixin.dynamodb_user_pk,
            sk=question_sk,
            attributes={
                DynamoDBKeySchema.GSI2_PK.value: dest_chat_gsi2_pk,
                DynamoDBKeySchema.GSI2_SK.value: dest_message_gsi2_sk,
            },
        )

    @staticmethod
    def _get_dest_chat_gsi2_pk(dest_chat_id: str) -> str:
        """Gets the destination chat GSI2 PK."""
        return DynamoDBFormatter.prefix_dest_chat_gsi2_pk(dest_chat_id=dest_chat_id)

    @staticmethod
    def _get_dest_message_gsi2_sk(dest_message_id: str) -> str:
        """Gets the destination message GSI2 SK."""
        return DynamoDBFormatter.prefix_dest_message_gsi2_sk(
            dest_message_id=dest_message_id,
        )

    async def _get_destination(self) -> Tuple[str, str]:
        """Retrieves the destination chat and topic from the database."""
        destination_chat = await self.dynamodb_mixin.get_destination_chat()
        destination_chat_topic = await self.dynamodb_mixin.get_destination_chat_topic()
        return destination_chat, destination_chat_topic

    def _format_question_message(self, question_data: dict) -> str:
        """Formats the question message."""
        db_attribute_labels = self.state_handler.config.db_attribute_labels
        return "\n".join(
            [
                f"**{label}**{question_data[state_name]}"
                for state_name, label in db_attribute_labels.items()
                if state_name in question_data
            ]
        )

    async def _send_question_to_destination(
        self, question_message: str, destination_chat: str, destination_chat_topic: str
    ) -> int:
        """Sends the question to the destination chat."""
        sent_message = await self.telethon_client.send_message(
            entity=int(destination_chat),
            message=question_message,
            reply_to=int(destination_chat_topic),
            link_preview=False,
        )
        return sent_message.id


class ConversationFlowHandlers(DynamoDBMixin):
    """A Class containing handlers for the conversation flow state machine."""

    def __init__(
        self,
        config: StateMachineConfig,
        user_id: str,
        dynamodb_crud_manager: DynamoDBCrudManager,
        telethon_event: NewMessage.Event | CallbackQuery.Event,
        transition_event: AsyncEventData | None = None,
    ):
        super().__init__(dynamodb_crud_manager, user_id)
        self.state_handler = StateHandler(config)
        self.question_handler = QuestionHandler(
            dynamodb_crud_manager=dynamodb_crud_manager,
            telethon_event=telethon_event,
            user_id=user_id,
            dynamodb_mixin=self,
            state_handler=self.state_handler,
        )
        self.telethon_event = telethon_event
        self.telethon_client: TelegramClient = telethon_event.client
        self._transition_event = transition_event
        self._dest_state = ""
        self._dest_state_inline_buttons = []

    @property
    def transition_event(self) -> AsyncEventData:
        """Get the transition event."""
        assert self._transition_event is not None, "Transition event is not set."
        return self._transition_event

    async def prepare_event(self, event: AsyncEventData):
        """Sets the transition event."""
        self._transition_event = event

    async def before_state_change(
        self, *args
    ):  # pylint: disable=unused-argument
        """Sets the destination state and inline buttons."""
        self._dest_state = self.transition_event.transition.dest
        self._dest_state_inline_buttons = self._strings_to_inline_buttons(
            self.state_handler.get_state_inline_buttons(self._dest_state), rtl=True
        )

    async def send_prompt_message(
        self, *args
    ):  # pylint: disable=unused-argument
        """Sends a prompt message to the user."""
        await self._send_message(
            message=self.state_handler.get_state_message(self._dest_state)
        )

    async def send_prompt_message_with_inline_buttons(
        self, *args
    ):  # pylint: disable=unused-argument
        """Sends a prompt message to the user with inline buttons."""
        await self._send_message(
            message=self.state_handler.get_state_message(self._dest_state),
            buttons=self._dest_state_inline_buttons,
        )

    async def edit_prompt_message_with_inline_buttons(
        self, *args
    ):  # pylint: disable=unused-argument
        """Edits the prompt message with inline buttons."""
        await self._edit_message(
            message=self.state_handler.get_state_message(self._dest_state),
            buttons=self._dest_state_inline_buttons,
        )

    async def edit_prompt_message(
        self, *args
    ):  # pylint: disable=unused-argument
        """Edits the prompt message with inline buttons."""
        await self._edit_message(
            message=self.state_handler.get_state_message(self._dest_state),
        )

    async def proccess_question_submission(
        self, *args
    ):  # pylint: disable=unused-argument
        """Processes the user's question submission."""
        await self.question_handler.process_question_submission(self.transition_event)

    async def update_user_state_in_db(
        self, *args
    ):  # pylint: disable=unused-argument
        """Updates the user's state in the database."""
        state = self.transition_event.model.state  # type: ignore
        await super().update_user_state_in_db(state)

    async def store_user_input_in_db(
        self, *args
    ):  # pylint: disable=unused-argument
        """Stores the user's input in the database."""
        user_input = await self._get_user_input()
        src_state = self.transition_event.transition.source
        await super().store_user_input_in_db(src_state, user_input)

    async def set_destination_chat(
        self, *args
    ):  # pylint: disable=unused-argument
        """Sets the destination chat for the user based on the destination state."""
        destination_chat_id = self.state_handler.get_state_destination_chat(
            self._dest_state
        )
        await super().store_destination_chat(destination_chat_id)

    async def set_destination_chat_topic(
        self, *args
    ):  # pylint: disable=unused-argument
        """Sets the destination chat topic for the user based on the destination state."""
        destination_chat_topic = self.state_handler.get_state_destination_chat_topic(
            self._dest_state
        )
        await super().store_destination_chat_topic(destination_chat_topic)

    async def _send_message(
        self, message: str, buttons: InlineButtons | list[InlineButtons] | None = None
    ):
        """Sends a message to the user."""
        await self.telethon_event.respond(message=message, buttons=buttons)

    async def _edit_message(
        self, message: str, buttons: InlineButtons | list[InlineButtons] | None = None
    ):
        """Edits the message sent to the user."""
        await self.telethon_event.edit(message, buttons=buttons)

    def _strings_to_inline_buttons(
        self,
        strings: StateInlineButtonsData,
        rtl: bool = False,
    ) -> InlineButtons | list[InlineButtons]:
        """Converts a list of strings or a list of lists of strings
        into a list of Telethon inline buttons."""
        if rtl:
            strings = self._reverse_nested_structure(strings)

        if isinstance(strings[0], list):
            # List of lists of strings (representing rows)
            return [
                [Button.inline(button, button) for button in row] for row in strings
            ]
        else:
            # List of strings (single row of buttons)
            return [Button.inline(button) for button in strings]

    @staticmethod
    def _reverse_nested_structure(
        nested_structure: list[list[str] | str],
    ) -> list[list[str] | str]:
        """Reverses the order of elements in each row of a nested structure."""
        return [row[::-1] if isinstance(row, list) else row for row in nested_structure]

    async def _get_user_input(self) -> str:
        """Retrieves the user's input from the event."""
        if isinstance(self.telethon_event, CallbackQuery.Event):
            return self.telethon_event.data.decode("utf-8")
        if isinstance(self.telethon_event, NewMessage.Event):
            return self.telethon_event.message.text
        return ""
