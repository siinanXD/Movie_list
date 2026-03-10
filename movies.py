"""
movies.py

Main application file for the movie database project.

This module is responsible for:
- displaying the menu
- validating user input
- calling the SQL storage layer
- showing movie statistics
- searching and filtering movies
"""

import random
import statistics
import requests
import movie_storage_sql as storage
import omdb_api


def print_menu() -> None:
    """
    Print the main menu of the application.
    """
    print()
    print("*" * 10, "My Movies Database", "*" * 10)
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
    print("9. Filter movies by minimum rating")
    print("*" * 36)


def prompt_non_empty_string(message: str) -> str:
    """
    Prompt the user until a non-empty string is entered.

    Args:
        message: The message shown to the user.

    Returns:
        str: A non-empty string.
    """
    while True:
        value = input(message).strip()
        if value:
            return value

        print("Input cannot be empty.")


def prompt_int(message: str, min_value: int | None = None) -> int:
    """
    Prompt the user until a valid integer is entered.

    Args:
        message: The message shown to the user.
        min_value: Optional minimum accepted value.

    Returns:
        int: The validated integer.
    """
    while True:
        value = input(message).strip()

        try:
            number = int(value)

            if min_value is not None and number < min_value:
                print(f"Please enter a number greater than or equal to {min_value}.")
                continue

            return number
        except ValueError:
            print("Please enter a valid whole number.")


def prompt_float(
    message: str,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    """
    Prompt the user until a valid float is entered.

    Args:
        message: The message shown to the user.
        min_value: Optional minimum accepted value.
        max_value: Optional maximum accepted value.

    Returns:
        float: The validated float.
    """
    while True:
        value = input(message).strip()

        try:
            number = float(value)

            if min_value is not None and number < min_value:
                print(f"Please enter a number greater than or equal to {min_value}.")
                continue

            if max_value is not None and number > max_value:
                print(f"Please enter a number less than or equal to {max_value}.")
                continue

            return number
        except ValueError:
            print("Please enter a valid number.")


def get_all_movies() -> dict:
    """
    Retrieve all movies from storage.

    Returns:
        dict: All movies from the database.
    """
    return storage.list_movies()


def command_list_movies() -> None:
    """
    Retrieve and display all movies from the database.
    """
    movies = get_all_movies()

    if not movies:
        print("No movies found.")
        return

    print(f"\n{len(movies)} movies in total:\n")

    for title, data in movies.items():
        print(f"{title} ({data['year']}): {data['rating']}")


def command_add_movie() -> None:
    """
    Prompt the user for movie details and add the movie to the database.
    """
    title = prompt_non_empty_string("Enter new movie name: ")
    year = prompt_int("Enter movie year: ", min_value=1888)
    rating = prompt_float("Enter movie rating (0-10): ", min_value=0.0, max_value=10.0)

    storage.add_movie(title, year, rating)


def command_delete_movie() -> None:
    """
    Prompt the user for a movie title and delete it from the database.
    """
    title = prompt_non_empty_string("Enter movie name to delete: ")
    storage.delete_movie(title)


def command_update_movie() -> None:
    """
    Prompt the user for a movie title and a new rating, then update it.
    """
    title = prompt_non_empty_string("Enter movie name to update: ")
    rating = prompt_float(
        "Enter new movie rating (0-10): ",
        min_value=0.0,
        max_value=10.0,
    )

    storage.update_movie(title, rating)


def command_statistics() -> None:
    """
    Calculate and display movie statistics.
    """
    movies = get_all_movies()

    if not movies:
        print("No movies found.")
        return

    ratings = [movie_data["rating"] for movie_data in movies.values()]
    average_rating = statistics.mean(ratings)
    median_rating = statistics.median(ratings)

    best_movie = max(
        movies.items(),
        key=lambda item: item[1]["rating"],
    )
    worst_movie = min(
        movies.items(),
        key=lambda item: item[1]["rating"],
    )

    print("\nMovie Statistics")
    print(f"Average rating: {average_rating:.2f}")
    print(f"Median rating: {median_rating:.2f}")
    print(
        f"Best movie: {best_movie[0]} "
        f"({best_movie[1]['year']}), {best_movie[1]['rating']}"
    )
    print(
        f"Worst movie: {worst_movie[0]} "
        f"({worst_movie[1]['year']}), {worst_movie[1]['rating']}"
    )


def command_random_movie() -> None:
    """
    Display a random movie from the database.
    """
    movies = get_all_movies()

    if not movies:
        print("No movies found.")
        return

    title = random.choice(list(movies.keys()))
    data = movies[title]

    print(f"Your random movie: {title} ({data['year']}): {data['rating']}")


def command_search_movie() -> None:
    """
    Search for a movie by title.

    The search is case-insensitive and matches partial titles.
    """
    movies = get_all_movies()

    if not movies:
        print("No movies found.")
        return

    search_term = prompt_non_empty_string("Enter part of movie name: ").lower()

    matching_movies = {
        title: data
        for title, data in movies.items()
        if search_term in title.lower()
    }

    if not matching_movies:
        print("No matching movies found.")
        return

    print(f"\nFound {len(matching_movies)} matching movie(s):\n")

    for title, data in matching_movies.items():
        print(f"{title} ({data['year']}): {data['rating']}")


def command_movies_sorted_by_rating() -> None:
    """
    Display all movies sorted by rating from highest to lowest.
    """
    movies = get_all_movies()

    if not movies:
        print("No movies found.")
        return

    sorted_movies = sorted(
        movies.items(),
        key=lambda item: item[1]["rating"],
        reverse=True,
    )

    print("\nMovies sorted by rating:\n")

    for title, data in sorted_movies:
        print(f"{title} ({data['year']}): {data['rating']}")


def command_filter_by_minimum_rating() -> None:
    """
    Display all movies with a rating greater than or equal to a minimum value.
    """
    movies = get_all_movies()

    if not movies:
        print("No movies found.")
        return

    minimum_rating = prompt_float(
        "Enter minimum rating (0-10): ",
        min_value=0.0,
        max_value=10.0,
    )

    filtered_movies = {
        title: data
        for title, data in movies.items()
        if data["rating"] >= minimum_rating
    }

    if not filtered_movies:
        print(f"No movies found with rating >= {minimum_rating}.")
        return

    sorted_movies = sorted(
        filtered_movies.items(),
        key=lambda item: item[1]["rating"],
        reverse=True,
    )

    print(f"\nMovies with rating >= {minimum_rating}:\n")

    for title, data in sorted_movies:
        print(f"{title} ({data['year']}): {data['rating']}")


def execute_choice(choice: str) -> bool:
    """
    Execute the selected menu command.

    Args:
        choice: The user's menu choice.

    Returns:
        bool: False if the program should exit, otherwise True.
    """
    actions = {
        "1": command_list_movies,
        "2": command_add_movie,
        "3": command_delete_movie,
        "4": command_update_movie,
        "5": command_statistics,
        "6": command_random_movie,
        "7": command_search_movie,
        "8": command_movies_sorted_by_rating,
        "9": command_filter_by_minimum_rating,
    }

    if choice == "0":
        print("Bye!")
        return False

    action = actions.get(choice)

    if action is None:
        print("Invalid choice. Please try again.")
        return True

    action()
    return True


def command_add_movie() -> None:
    """Add a movie using OMDb API."""
    title = input("Enter movie name: ").strip()

    data = omdb_api.fetch_movie(title)

    if data is None:
        return

    title = data["Title"]

    year = int(data["Year"][:4])

    rating_text = data.get("imdbRating", "0")
    rating = float(rating_text) if rating_text != "N/A" else 0.0

    poster_url = data.get("Poster", "")

    storage.add_movie(title, year, rating, poster_url)


def main() -> None:
    """
    Run the main application loop.
    """
    should_continue = True

    while should_continue:
        print_menu()
        choice = input("Enter choice (0-9): ").strip()
        should_continue = execute_choice(choice)


if __name__ == "__main__":
    main()