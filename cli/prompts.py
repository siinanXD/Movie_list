"""CLI prompt helper functions."""


def prompt_choice(prompt: str, min_value: int = 0, max_value: int = 0) -> int:
    """
    Prompt the user for a numeric choice within a range.

    Args:
        prompt: The message to display.
        min_value: Minimum allowed value.
        max_value: Maximum allowed value.

    Returns:
        The validated integer choice.
    """
    while True:
        user_input = input(prompt).strip()

        if not user_input.isdigit():
            print("Invalid input. Please enter a number.")
            continue

        choice = int(user_input)

        if choice < min_value or choice > max_value:
            print(f"Please enter a number between {min_value} and {max_value}.")
            continue

        return choice


def prompt_int(prompt: str, min_value: int, max_value: int) -> int:
    """Prompt the user for an integer within a range."""
    while True:
        user_input = input(prompt).strip()

        if not user_input.isdigit():
            print("Invalid input. Please enter a number.")
            continue

        value = int(user_input)

        if value < min_value or value > max_value:
            print(f"Please enter a value between {min_value} and {max_value}.")
            continue

        return value


def prompt_float(prompt: str, min_value: float, max_value: float) -> float:
    """Prompt the user for a float within a range."""
    while True:
        user_input = input(prompt).strip()

        try:
            value = float(user_input)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if value < min_value or value > max_value:
            print(f"Please enter a value between {min_value} and {max_value}.")
            continue

        return value