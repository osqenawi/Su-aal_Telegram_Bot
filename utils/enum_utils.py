from enum import Enum

def get_next_enum_member(current_member: Enum) -> Enum:
    """
    Get the next Enum member based on the current Enum member.

    Parameters:
        current_member (Enum): The current Enum member.

    Returns:
        Enum: The next Enum member.

    Example:
        >>> class MyEnum(Enum):
        ...     FIRST = 1
        ...     SECOND = 2
        ...     THIRD = 3
        ...     FOURTH = 4
        >>> current_member = MyEnum.FIRST
        >>> next_member = get_next_enum_member(current_member)
        >>> print(next_member)
        MyEnum.SECOND
    """
    members = current_member.__class__.__members__
    current_index = list(members).index(current_member.name)
    next_index = (current_index + 1) % len(members)
    next_member_name = list(members)[next_index]
    return current_member.__class__[next_member_name]