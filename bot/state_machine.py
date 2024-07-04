"""../bot/state_machine.py"""

from transitions.extensions.asyncio import HierarchicalAsyncMachine

from config.state_machine.state_machine_config import StateMachineConfig


class ConversationFlowStateMachine:
    """A class representing a conversation flow state machine."""

    def __init__(self, config: StateMachineConfig):
        self.config = config
        self.machine = self._create_state_machine()

    def _create_state_machine(self):
        return HierarchicalAsyncMachine(
            model=None,
            states=self.config.states,
            transitions=self.config.transitions,
            queued="model",
            send_event=True,
            auto_transitions=False,
            prepare_event="prepare_event",
            before_state_change="before_state_change",
            after_state_change="update_user_state_in_db",
        )

    def add_conversation(self, model, state: str):
        """Adds a conversation as a model to the state machine."""
        self.machine.add_model(model, initial=state)

    def remove_conversation(self, model):
        """Removes a conversation from the state machine."""
        self.machine.remove_model(model)

    def __getattr__(self, name):
        """Delegate attribute access to the underlying state machine."""
        return getattr(self.machine, name)


class ConversationFlowStateMachineManager:
    """A class representing a singleton manager for the conversation flow state machine."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: StateMachineConfig):
        self._config = config

        self.machine = self._setup_state_machine()

    def _setup_state_machine(self):
        """Creates and sets up the state machine."""
        return ConversationFlowStateMachine(config=self._config)
