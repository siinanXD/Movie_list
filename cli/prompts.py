"""Reusable input prompt helpers for CLI interaction."""


def prompt_non_empty_string(message: str) -> str:
    """Prompt until a non-empty string is entered."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Input cannot be empty.")



def prompt_optional_string(message: str) -> str:
    """Prompt once and return the raw stripped value, including empty input."""
    return input(message).strip()



def prompt_choice(message: str, min_value: int | None = None) -> int:
    """Prompt until a valid integer choice is entered."""
    while True:
        value = input(message).strip()
        try:
            number = int(value)
        except ValueError:
            print("Please enter a valid whole number.")
            continue

        if min_value is not None and number < min_value:
            print(f"Please enter a number greater than or equal to {min_value}.")
            continue

        return number



def prompt_float(
    message: str,
    min_value: float | None = None,
    max_value: float | None = None,
    allow_empty: bool = False,
) -> float | None:
    """Prompt until a valid float is entered, or return None when empty is allowed."""
    while True:
        value = input(message).strip()

        if allow_empty and value == "":
            return None

        try:
            number = float(value)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if min_value is not None and number < min_value:
            print(f"Please enter a number greater than or equal to {min_value}.")
            continue

        if max_value is not None and number > max_value:
            print(f"Please enter a number less than or equal to {max_value}.")
            continue

        return number



def prompt_int(
    message: str,
    min_value: int | None = None,
    allow_empty: bool = False,
) -> int | None:
    """Prompt until a valid integer is entered, or return None when empty is allowed."""
    while True:
        value = input(message).strip()

        if allow_empty and value == "":
            return None

        try:
            number = int(value)
        except ValueError:
            print("Please enter a valid whole number.")
            continue

        if min_value is not None and number < min_value:
            print(f"Please enter a number greater than or equal to {min_value}.")
            continue

        return number
