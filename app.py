"""Core application orchestration for the movie app."""

from __future__ import annotations

from pathlib import Path

from cli.menu import print_menu
from cli.prompts import prompt_choice
from services import movie_service, stats_service, website_service
from storage import movie_storage_sql as storage

APP_TITLE = "My Movie App"
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "static" / "index_template.html"
OUTPUT_DIR = BASE_DIR / "website"


class MovieApp:
    """Coordinate user selection, menu handling, and app actions."""

    def __init__(self) -> None:
        self.active_user: dict | None = None

    def run(self) -> None:
        """Start the application loop."""
        self.active_user = self.select_user()

        should_continue = True
        while should_continue:
            print_menu(active_user_name=self.active_user["name"])
            choice = prompt_choice("Enter choice (0-11): ")
            should_continue = self.execute_choice(choice)

    def select_user(self) -> dict:
        """Select an existing user or create a new one."""
        while True:
            users = storage.list_users()

            print()
            print("Welcome to the Movie App!")
            print()
            print("Select a user:")

            for index, user in enumerate(users, start=1):
                print(f"{index}. {user['name']}")

            print(f"{len(users) + 1}. Create new user")

            choice = prompt_choice("Enter choice: ", min_value=1)

            if choice <= len(users):
                selected_user = users[choice - 1]
                print(f"\nWelcome back, {selected_user['name']}!")
                return selected_user

            if choice == len(users) + 1:
                created_user = movie_service.create_user()
                if created_user is not None:
                    return created_user
                continue

            print("Invalid choice. Please try again.")

    def execute_choice(self, choice: int) -> bool:
        """Execute the selected action and return whether to continue."""
        if choice == 0:
            print("Bye!")
            return False

        user_id = self._get_active_user_id()
        user_name = self.active_user["name"]

        actions = {
            1: lambda: movie_service.list_movies(user_id=user_id, user_name=user_name),
            2: lambda: movie_service.add_movie(user_id=user_id, user_name=user_name),
            3: lambda: movie_service.delete_movie(user_id=user_id),
            4: lambda: movie_service.update_movie(user_id=user_id),
            5: lambda: stats_service.show_statistics(user_id=user_id, user_name=user_name),
            6: lambda: movie_service.show_random_movie(user_id=user_id, user_name=user_name),
            7: lambda: movie_service.search_movie(user_id=user_id, user_name=user_name),
            8: lambda: movie_service.show_movies_sorted_by_rating(user_id=user_id, user_name=user_name),
            9: lambda: website_service.generate_website(
                app_title=APP_TITLE,
                template_path=TEMPLATE_PATH,
                output_dir=OUTPUT_DIR,
                user=self.active_user,
                movies=movie_service.get_all_movies(user_id),
            ),
            10: lambda: movie_service.filter_movies_by_minimum_rating(
                user_id=user_id,
                user_name=user_name,
            ),
            11: self.switch_user,
        }

        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please try again.")
            return True

        action()
        return True

    def switch_user(self) -> None:
        """Switch the active user."""
        self.active_user = self.select_user()

    def _get_active_user_id(self) -> int:
        """Return the current active user's id."""
        if self.active_user is None:
            raise ValueError("No active user selected.")
        return self.active_user["id"]
