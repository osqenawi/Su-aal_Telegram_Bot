from enum import Enum

from .models import flow_steps
from utils.enum_utils import get_next_element, get_next_element_with_callback


# Define an enumeration for the different states in the conversation flow
States = Enum("States", list(flow_steps.keys()))


# We set the function get_next_enum_member as an attribute 'get_next_element' of the States Enum, which allows
# us to call it directly on any States member to get the next Enum member in the sequence.
States.get_next_element = get_next_element
States.get_next_element_with_callback = get_next_element_with_callback


# Add dynamic attributes for members of the States enumeration using the flow_steps dictionary
for state_name, state_data in flow_steps.items():
    # Get the corresponding enumeration member
    state_member = getattr(States, state_name)

    # Set attributes for the state_member using the state_data dictionary
    for key, value in state_data.items():
        setattr(state_member, key, value)

# Now, you can access the attributes for each States member easily
# print(States.START_AND_CHOOSE_BATCH.input_type)


