from enum import Enum, EnumMeta
from typing import Callable, TypeVar, Any


# Define the TypeVar for the generic type parameter T
T = TypeVar('T', bound=Enum)


class EnumMetaWithNext(EnumMeta):
    """
    Metaclass for enhancing Enum classes with additional utility functions.

    This metaclass provides two utility functions:
    - `get_next_element`: Get the next element in the enum sequence.
    - `get_next_element_with_callback`: Get the next element in the enum sequence that satisfies the given condition.

    Usage:
    1. Inherit an Enum class from this metaclass.
    2. The Enum class will automatically have access to the `get_next_element` and `get_next_element_with_callback`
       utility functions.

    Example:
    ```python
    from enum import Enum

    class MyEnum(Enum, metaclass=EnumMetaWithNext):
        # Enum members and values here

    # Now you can use `MyEnum.get_next_element()` and `MyEnum.get_next_element_with_callback()`.
    ```

    """

    def get_next_element(self: T, enum_instance: T) -> T:
        """
        Get the next element in the enum sequence.

        Parameters:
            enum_instance (T): The current enum instance.

        Returns:
            T: The next enum instance.
        """
        members = list(self)
        idx = (members.index(enum_instance) + 1) % len(members)
        return members[idx]

    def find_next_matching_element(self: T, enum_instance: T, callback: Callable[[T, Any], bool], *args: Any, **kwargs: Any) -> T:
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
        next_instance = enum_instance
        for _ in range(len(self)):
            if callback(next_instance, *args, **kwargs):
                return next_instance
            next_instance = self.get_next_element(next_instance)
        raise ValueError("No satisfying condition found in enum.")

    def get_next_element_with_callback(self: T, enum_instance: T, callback: Callable[[T, Any], bool], *args: Any, **kwargs: Any) -> T:
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
        return self.find_next_matching_element(enum_instance, callback, *args, **kwargs)


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
