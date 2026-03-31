"""Application controller for the movie app."""

from pathlib import Path

from cli.menu import print_menu
from cli.prompts import prompt_choice
from services import movie_service, stats_service, website_service
from storage import movie_storage_sql as storage

APP_TITLE = "My Movie App"
TEMPLATE_PATH = Path("static/index_template.html")
OUTPUT_DIR = Path("website")


class MovieApp:
    """Main application class."""

    def __init__(self) -> None:
        """Initialize the app and select the active user."""
        storage.initialize_database()
        self.active_user: dict | None = self.select_user()

    def select_user(self) -> dict:
        """Select an existing user or create a new one."""
        users = storage.list_users()

        if users:
            print("\nUsers:")
            for index, user in enumerate(users, start=1):
                print(f"{index}. {user['name']}")
            print("0. Create new user")

            while True:
                choice = prompt_choice("Choose a user: ", 0, len(users))

                if choice == 0:
                    return self.create_user()

                selected_user = users[choice - 1]
                print(f"\nActive user: {selected_user['name']}")
                return selected_user

        return self.create_user()

    def create_user(self) -> dict:
        """Create a new user and return it."""
        while True:
            name = input("Enter a new username: ").strip()
            if not name:
                print("Username cannot be empty.")
                continue

            user_id = storage.add_user(name)
            if user_id is None:
                print("This username already exists. Please choose another.")
                continue

            user = {"id": user_id, "name": name}
            print(f"\nUser '{name}' created and selected.")
            return user

    def switch_user(self) -> None:
        """Switch the active user."""
        self.active_user = self.select_user()

    def _get_active_user_id(self) -> int:
        """Return the active user id."""
        if self.active_user is None:
            raise ValueError("No active user selected.")
        return self.active_user["id"]

    def generate_website_for_active_user(self) -> None:
        """Generate the website after backfilling missing metadata."""
        user_id = self._get_active_user_id()

        movie_service.backfill_missing_movie_metadata(user_id)

        website_service.generate_website(
            app_title=APP_TITLE,
            template_path=TEMPLATE_PATH,
            output_dir=OUTPUT_DIR,
            user=self.active_user,
            movies=movie_service.get_all_movies(user_id),
        )

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
            5: lambda: stats_service.show_statistics(
                user_id=user_id,
                user_name=user_name,
            ),
            6: lambda: movie_service.show_random_movie(
                user_id=user_id,
                user_name=user_name,
            ),
            7: lambda: movie_service.search_movie(
                user_id=user_id,
                user_name=user_name,
            ),
            8: lambda: movie_service.show_movies_sorted_by_rating(
                user_id=user_id,
                user_name=user_name,
            ),
            9: self.generate_website_for_active_user,
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

    def run(self) -> None:
        """Run the application loop."""
        while True:
            print_menu(self.active_user["name"])
            choice = prompt_choice("Enter choice: ", 0, 11)
            should_continue = self.execute_choice(choice)
            if not should_continue:
                break