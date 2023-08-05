from enum import Enum
from typing import TypeVar, Callable, Any


T = TypeVar('T', bound=Enum)


def get_next_element(enum_instance: T) -> T:
    """
    Get the next element in the enum sequence.

    Parameters:
        enum_instance (T): The current enum instance.

    Returns:
        T: The next enum instance.
    """
    members = list(enum_instance.__class__)
    idx = (members.index(enum_instance) + 1) % len(members)
    return members[idx]


def find_next_matching_element(enum_instance: T, callback: Callable[[T, Any], bool], *args: Any, **kwargs: Any) -> T:
    """
    Find the next element in the enum sequence that satisfies the given condition.

    Parameters:
        enum_instance (T): The current enum instance.
        callback (Callable[[T, Any], bool]): A function that takes the current enum instance and returns a boolean.
        *args (Any): Additional positional arguments to pass to the callback function.
        **kwargs (Any): Additional keyword arguments to pass to the callback function.

    Returns:
        T: The next enum instance that satisfies the condition.

    Raises:
        ValueError: If no satisfying condition is found in the enum.
    """
    for _ in range(len(enum_instance.__class__)):
        if callback(enum_instance, *args, **kwargs):
            return enum_instance
        enum_instance = get_next_element(enum_instance)
    raise ValueError("No satisfying condition found in enum.")


def get_next_element_with_callback(enum_instance: T, callback: Callable[[T, Any], bool], *args: Any, **kwargs: Any) -> T:
    """
    Get the next element in the enum sequence that satisfies the given condition.

    Parameters:
        enum_instance (T): The current enum instance.
        callback (Callable[[T, Any], bool]): A function that takes the current enum instance and returns a boolean.
        *args (Any): Additional positional arguments to pass to the callback function.
        **kwargs (Any): Additional keyword arguments to pass to the callback function.

    Returns:
        T: The next enum instance that satisfies the condition.

    Raises:
        ValueError: If no satisfying condition is found in the enum.
    """
    return find_next_matching_element(enum_instance, callback, *args, **kwargs)
