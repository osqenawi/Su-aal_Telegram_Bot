"""../bot/conversation_flow.py"""

from telethon.events import CallbackQuery, NewMessage
from telethon.tl.types import KeyboardButtonCallback
from transitions.extensions.asyncio import AsyncEventData

from bot.handlers.conversation_flow_handlers import ConversationFlowHandlers
from bot.services.dynamodb_constants import DynamoDBAttributes
from bot.services.dynamodb_crud_manager import DynamoDBCrudManager
from bot.state_machine import (
    ConversationFlowStateMachine,
    ConversationFlowStateMachineManager,
)
from config.state_machine.state_machine_config import StateMachineConfig

InlineButtons = list[KeyboardButtonCallback]


class ConversationFlow(ConversationFlowHandlers):
    """A class representing a model for the conversation flow state machine."""

    _MACHINE: ConversationFlowStateMachine

    def __init__(
        self,
        user_id: str,
        dynamodb_crud_manager: DynamoDBCrudManager,
        telethon_event: CallbackQuery.Event | NewMessage.Event,
    ):
        super().__init__(
            config=self._MACHINE.config,
            user_id=user_id,
            dynamodb_crud_manager=dynamodb_crud_manager,
            telethon_event=telethon_event,
            transition_event=None,
        )
        self.transition_event: AsyncEventData  # Set by the set_transition_event method by the state machine

    @classmethod
    def config(cls, config: StateMachineConfig):
        """Configures the state machine."""
        cls._MACHINE = ConversationFlowStateMachineManager(config=config).machine

    @property
    def _state_machine_config(self):
        """Get the state machine configuration."""
        return self._MACHINE.config

    @property
    async def user_state(self):
        """Get the user state, retrieving it from the database if not already available."""
        user_state = await self._get_user_state_from_db()
        return user_state or self._state_machine_config.initial_state

    async def _get_user_state_from_db(self) -> str | None:
        """Retrieves the user's state from the database."""
        response = await self.dynamodb_crud_manager.get_attribute(
            attribute=DynamoDBAttributes.USER_STATE.value,
            pk=self.dynamodb_user_pk,
            sk=self.dynamodb_user_sk,
        )
        return response if isinstance(response, str) else None

    async def trigger_start(self):
        """Triggers the start event."""
        await self._clear_user_inputs_in_db()
        await self.trigger(self._state_machine_config.initial_trigger)   # type: ignore  # pylint: disable=no-member

    async def trigger_callback(self, data: str):
        """Triggers an event based on the callback data."""
        await self.trigger(data)  # type: ignore  # pylint: disable=no-member

    async def trigger_next_state(self):
        """Triggers the next state in the conversation flow."""
        triggers: list = await self._get_valid_next_triggers()
        if len(triggers) == 1:
            await self.trigger(triggers[0])  # type: ignore  # pylint: disable=no-member

    async def _clear_user_inputs_in_db(self):
        """Clears the user's inputs in the database."""
        to_delete = [
            DynamoDBAttributes.USER_INPUTS.value,
            DynamoDBAttributes.DESTINATION_CHAT.value,
            DynamoDBAttributes.DESTINATION_CHAT_TOPIC.value,
            DynamoDBAttributes.USER_STATE.value,
        ]
        await self.dynamodb_crud_manager.delete_attributes(
            pk=self.dynamodb_user_pk,
            sk=self.dynamodb_user_sk,
            attributes=to_delete,
        )

    async def _get_valid_next_triggers(self) -> list:
        """Returns the valid next triggers from the current state."""
        current_state = await self.user_state
        return [
            trigger
            for trigger in self._MACHINE.get_triggers(current_state)
            if trigger.startswith("@")
        ]

    async def setup_conversation(self):
        """Sets up the conversation by adding it to the state machine models."""
        assert (
            self._MACHINE is not None
        ), "The state machine must be configured first using the `config` method."
        self._MACHINE.add_conversation(model=self, state=await self.user_state)

    async def cleanup(self):
        """Cleans up the conversation by removing it from the state machine models."""
        self._MACHINE.remove_conversation(self)

    async def __aenter__(self):
        await self.setup_conversation()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.cleanup()
