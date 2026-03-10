"""
movies.py

Main application file for the movie database project.

Features:
- list movies
- add movie via OMDb API
- delete movie
- update movie rating
- show statistics
- show random movie
- search movie
- sort movies by rating
- generate website from template
- filter movies by minimum rating
"""

from html import escape
from pathlib import Path
import random
import statistics

from storage import movie_storage_sql as storage
from api import omdb_api

APP_TITLE = "My Movie App"
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "index_template.html"
OUTPUT_HTML_PATH = BASE_DIR / "index.html"


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
    print("9. Generate website")
    print("10. Filter movies by minimum rating")
    print("*" * 36)


def prompt_non_empty_string(message: str) -> str:
    """
    Prompt the user until a non-empty string is entered.

    Args:
        message: The input prompt message.

    Returns:
        str: A non-empty user input string.
    """
    while True:
        user_input = input(message).strip()

        if user_input:
            return user_input

        print("Input cannot be empty.")


def prompt_float(
    message: str,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    """
    Prompt the user until a valid float is entered.

    Args:
        message: The input prompt message.
        min_value: Optional minimum allowed value.
        max_value: Optional maximum allowed value.

    Returns:
        float: The validated float value.
    """
    while True:
        user_input = input(message).strip()

        try:
            value = float(user_input)

            if min_value is not None and value < min_value:
                print(f"Please enter a number greater than or equal to {min_value}.")
                continue

            if max_value is not None and value > max_value:
                print(f"Please enter a number less than or equal to {max_value}.")
                continue

            return value
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
    Display all movies from the database.
    """
    movies = get_all_movies()

    if not movies:
        print("No movies found.")
        return

    print(f"\n{len(movies)} movies in total:\n")

    for title, data in movies.items():
        print(f"{title} ({data['year']}): {data['rating']}")


def parse_year(year_text: str) -> int:
    """
    Parse the year returned by OMDb.

    OMDb may return values like:
    - 1997
    - 2016–2019
    - N/A

    Args:
        year_text: Year text from OMDb.

    Returns:
        int: Parsed year or 0 if parsing fails.
    """
    try:
        return int(year_text[:4])
    except (ValueError, TypeError):
        return 0


def parse_rating(rating_text: str) -> float:
    """
    Parse the IMDb rating returned by OMDb.

    Args:
        rating_text: Rating text from OMDb.

    Returns:
        float: Parsed rating or 0.0 if unavailable.
    """
    try:
        if rating_text == "N/A":
            return 0.0
        return float(rating_text)
    except (ValueError, TypeError):
        return 0.0


def command_add_movie() -> None:
    """
    Add a movie using only its title.

    The movie data is fetched automatically from the OMDb API.
    """
    movie_title = prompt_non_empty_string("Enter movie name: ")

    data = omdb_api.fetch_movie(movie_title)

    if data is None:
        return

    title = data.get("Title", movie_title)
    year = parse_year(data.get("Year", "0"))
    rating = parse_rating(data.get("imdbRating", "0"))
    poster_url = data.get("Poster", "")

    if poster_url == "N/A":
        poster_url = ""

    storage.add_movie(title, year, rating, poster_url)


def command_delete_movie() -> None:
    """
    Delete a movie from the database.
    """
    title = prompt_non_empty_string("Enter movie name to delete: ")
    storage.delete_movie(title)


def command_update_movie() -> None:
    """
    Update a movie rating manually.

    This command remains available, even though OMDb now provides real data.
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

    best_movie = max(movies.items(), key=lambda item: item[1]["rating"])
    worst_movie = min(movies.items(), key=lambda item: item[1]["rating"])

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
    Search for movies by a partial title match.
    """
    movies = get_all_movies()

    if not movies:
        print("No movies found.")
        return

    search_term = prompt_non_empty_string("Enter part of movie name: ").lower()

    matches = {
        title: data
        for title, data in movies.items()
        if search_term in title.lower()
    }

    if not matches:
        print("No matching movies found.")
        return

    print(f"\nFound {len(matches)} matching movie(s):\n")

    for title, data in matches.items():
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


def create_movie_html(title: str, year: int, poster_url: str) -> str:
    """
    Create the HTML block for a single movie card.

    Args:
        title: Movie title.
        year: Movie release year.
        poster_url: Poster image URL.

    Returns:
        str: HTML for one movie entry.
    """
    safe_title = escape(title)
    safe_year = escape(str(year))
    safe_poster_url = escape(poster_url)

    if not safe_poster_url:
        safe_poster_url = (
            "https://via.placeholder.com/200x300?text=No+Poster"
        )

    return f"""
        <div class="movie">
            <img class="movie-poster" src="{safe_poster_url}" alt="{safe_title}">
            <div class="movie-title">{safe_title}</div>
            <div class="movie-year">{safe_year}</div>
        </div>
    """.strip()


def generate_movies_grid(movies: dict) -> str:
    """
    Generate the complete movie grid HTML.

    Args:
        movies: Dictionary of movies.

    Returns:
        str: Combined HTML for all movie cards.
    """
    movie_items = []

    for title, data in movies.items():
        movie_html = create_movie_html(
            title=title,
            year=data["year"],
            poster_url=data.get("poster_url", ""),
        )
        movie_items.append(movie_html)

    return "\n".join(movie_items)


def generate_website() -> None:
    """
    Generate index.html from the HTML template and movie data.
    """
    movies = get_all_movies()

    if not TEMPLATE_PATH.exists():
        print("Template file 'index_template.html' was not found.")
        return

    template_content = TEMPLATE_PATH.read_text(encoding="utf-8")
    movie_grid = generate_movies_grid(movies)

    html_content = template_content.replace("__TEMPLATE_TITLE__", APP_TITLE)
    html_content = html_content.replace("__TEMPLATE_MOVIE_GRID__", movie_grid)

    OUTPUT_HTML_PATH.write_text(html_content, encoding="utf-8")
    print("Website was generated successfully.")


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
        "9": generate_website,
        "10": command_filter_by_minimum_rating,
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


def main() -> None:
    """
    Run the main application loop.
    """
    should_continue = True

    while should_continue:
        print_menu()
        choice = input("Enter choice (0-10): ").strip()
        should_continue = execute_choice(choice)


if __name__ == "__main__":
    main()