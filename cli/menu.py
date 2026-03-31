"""CLI menu rendering helpers."""


def print_menu(active_user_name: str | None = None) -> None:
    """Print the main application menu."""
    print()
    print("*" * 10, "My Movies Database", "*" * 10)

    if active_user_name:
        print(f"Active user: {active_user_name}")

    print("Menu:")
    print("0. Exit")
    print("1. List movies")
    print("2. Add movie")
    print("3. Delete movie")
    print("4. Update movie")
    print("5. Statistics")
    print("6. Random movie")
    print("7. Search movie")
    print("8. Movies sorted by rating")
    print("9. Generate website")
    print("10. Filter movies by minimum rating")
    print("11. Switch user")
    print("*" * 36)
