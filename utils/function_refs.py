from typing import List, Callable


def make_ref(refs_list: List[Callable] = []) -> Callable:
    def decorator(func: Callable) -> Callable:
        # Add the function reference to the refs_list
        refs_list.append(func)
        # Return the original function
        return func
    return decorator