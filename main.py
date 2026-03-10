"""
main.py

Main application file for the movie database project.

Features:
- user profiles
- add movies via OMDb API
- store movies in SQLite
- update movie notes
- generate user-specific websites
- display ratings, flags and IMDb links in the website
- website search bar as a bonus feature
"""

from html import escape
from pathlib import Path
import random
import statistics

from api import country_flags_api
from api import omdb_api
from storage import movie_storage_sql as storage

APP_TITLE = "My Movie App"

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "static" / "index_template.html"
OUTPUT_DIR = BASE_DIR / "website"

ACTIVE_USER: dict | None = None


def print_menu() -> None:
    """
    Print the main menu of the application.
    """
    print()
    print("*" * 10, "My Movies Database", "*" * 10)

    if ACTIVE_USER is not None:
        print(f"Active user: {ACTIVE_USER['name']}")

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


def prompt_non_empty_string(message: str) -> str:
    """
    Prompt the user until a non-empty string is entered.

    Args:
        message: The prompt message.

    Returns:
        str: Validated user input.
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
        message: The prompt message.
        min_value: Optional minimum value.

    Returns:
        int: Validated integer.
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
        message: The prompt message.
        min_value: Optional minimum value.
        max_value: Optional maximum value.

    Returns:
        float: Validated float.
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


def get_active_user_id() -> int:
    """
    Return the ID of the active user.

    Returns:
        int: Active user ID.
    """
    if ACTIVE_USER is None:
        raise ValueError("No active user selected.")

    return ACTIVE_USER["id"]


def get_all_movies() -> dict:
    """
    Return all movies for the active user.

    Returns:
        dict: Movie dictionary for the current user.
    """
    return storage.list_movies(get_active_user_id())


def parse_year(year_text: str) -> int:
    """
    Parse the OMDb year field.

    Args:
        year_text: Year text from OMDb.

    Returns:
        int: Parsed year or 0 if invalid.
    """
    try:
        return int(year_text[:4])
    except (ValueError, TypeError):
        return 0


def parse_rating(rating_text: str) -> float:
    """
    Parse the OMDb rating field.

    Args:
        rating_text: Rating text from OMDb.

    Returns:
        float: Parsed rating or 0.0 if invalid.
    """
    try:
        if rating_text == "N/A":
            return 0.0
        return float(rating_text)
    except (ValueError, TypeError):
        return 0.0


def extract_primary_country(country_text: str) -> str:
    """
    Extract the first country from the OMDb country field.

    Args:
        country_text: Raw OMDb country text, possibly comma-separated.

    Returns:
        str: First country name.
    """
    if not country_text:
        return ""

    return country_text.split(",")[0].strip()


def select_user() -> dict:
    """
    Let the user select an existing profile or create a new one.

    Returns:
        dict: The selected active user.
    """
    while True:
        users = storage.list_users()

        print()
        print("Welcome to the Movie App!")
        print()
        print("Select a user:")

        for index, user in enumerate(users, start=1):
            print(f"{index}. {user['name']}")

        print(f"{len(users) + 1}. Create new user")

        choice = prompt_int("Enter choice: ", min_value=1)

        if choice <= len(users):
            selected_user = users[choice - 1]
            print(f"\nWelcome back, {selected_user['name']}!")
            return selected_user

        if choice == len(users) + 1:
            new_name = prompt_non_empty_string("Enter new user name: ")
            created_user = storage.create_user(new_name)

            if created_user is None:
                print("A user with that name already exists.")
                continue

            print(f"\nUser '{created_user['name']}' created successfully.")
            return created_user

        print("Invalid choice. Please try again.")


def command_list_movies() -> None:
    """
    Display all movies for the active user.
    """
    movies = get_all_movies()

    if not movies:
        print(f"{ACTIVE_USER['name']}, your movie collection is empty.")
        return

    print(f"\n{len(movies)} movies in total:\n")

    for title, data in movies.items():
        note = data.get("note", "")
        country_flag = data.get("country_flag", "")
        country = data.get("country", "")
        rating = data.get("rating", 0.0)

        extras = []

        if country_flag:
            extras.append(f"{country_flag} {country}".strip())

        extras.append(f"Rating: {rating}")

        info_line = " | ".join(extras)

        if note:
            print(f"{title} ({data['year']}): {info_line} | Note: {note}")
        else:
            print(f"{title} ({data['year']}): {info_line}")


def command_add_movie() -> None:
    """
    Add a movie to the active user's collection using OMDb.
    """
    movie_title = prompt_non_empty_string("Enter movie name: ")

    data = omdb_api.fetch_movie(movie_title)

    if data is None:
        print("Could not retrieve movie information.")
        return

    title = data.get("Title", movie_title)
    year = parse_year(data.get("Year", "0"))
    rating = parse_rating(data.get("imdbRating", "0"))
    poster_url = data.get("Poster", "")
    imdb_id = data.get("imdbID", "")
    country = extract_primary_country(data.get("Country", ""))
    country_flag = country_flags_api.fetch_flag(country)

    if poster_url == "N/A":
        poster_url = ""

    was_added = storage.add_movie(
        user_id=get_active_user_id(),
        title=title,
        year=year,
        rating=rating,
        poster_url=poster_url,
        imdb_id=imdb_id,
        country=country,
        country_flag=country_flag,
    )

    if was_added:
        print(f"Movie '{title}' added to {ACTIVE_USER['name']}'s collection!")
    else:
        print(
            f"Movie '{title}' already exists in "
            f"{ACTIVE_USER['name']}'s collection."
        )


def command_delete_movie() -> None:
    """
    Delete a movie from the active user's collection.
    """
    title = prompt_non_empty_string("Enter movie name to delete: ")
    was_deleted = storage.delete_movie(get_active_user_id(), title)

    if was_deleted:
        print(f"Movie '{title}' deleted successfully.")
    else:
        print("Movie not found.")


def command_update_movie() -> None:
    """
    Update a personal movie note for the active user.
    """
    title = prompt_non_empty_string("Enter movie name: ")
    note = prompt_non_empty_string("Enter movie note: ")

    was_updated = storage.update_movie_note(
        user_id=get_active_user_id(),
        title=title,
        note=note,
    )

    if was_updated:
        print(f"Movie {title} successfully updated")
    else:
        print("Movie not found.")


def command_statistics() -> None:
    """
    Show movie statistics for the active user.
    """
    movies = get_all_movies()

    if not movies:
        print(f"{ACTIVE_USER['name']}, your movie collection is empty.")
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
    Display a random movie from the active user's collection.
    """
    movies = get_all_movies()

    if not movies:
        print(f"{ACTIVE_USER['name']}, your movie collection is empty.")
        return

    title = random.choice(list(movies.keys()))
    data = movies[title]

    print(f"Your random movie: {title} ({data['year']}): {data['rating']}")


def command_search_movie() -> None:
    """
    Search the active user's collection by partial movie title.
    """
    movies = get_all_movies()

    if not movies:
        print(f"{ACTIVE_USER['name']}, your movie collection is empty.")
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
    Display all movies for the active user sorted by rating.
    """
    movies = get_all_movies()

    if not movies:
        print(f"{ACTIVE_USER['name']}, your movie collection is empty.")
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
    Filter the active user's movies by minimum rating.
    """
    movies = get_all_movies()

    if not movies:
        print(f"{ACTIVE_USER['name']}, your movie collection is empty.")
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


def build_imdb_url(imdb_id: str) -> str:
    """
    Build a clickable IMDb URL for a movie.

    Args:
        imdb_id: IMDb id.

    Returns:
        str: IMDb URL or "#" if id is missing.
    """
    if not imdb_id:
        return "#"

    return f"https://www.imdb.com/title/{imdb_id}/"


def build_movie_grid(movies: dict) -> str:
    """
    Build the HTML movie grid for website generation.

    Args:
        movies: Movie dictionary for the active user.

    Returns:
        str: HTML string for all movie cards.
    """
    movie_cards = []

    for title, data in movies.items():
        year = data.get("year", "")
        rating = data.get("rating", 0.0)
        poster_url = data.get("poster_url", "")
        note = data.get("note", "")
        imdb_id = data.get("imdb_id", "")
        country = data.get("country", "")
        country_flag = data.get("country_flag", "")

        safe_title = escape(title)
        safe_year = escape(str(year))
        safe_rating = escape(f"{rating:.1f}")
        safe_note = escape(note)
        safe_country = escape(country)
        safe_flag = escape(country_flag)
        safe_poster_url = escape(poster_url) if poster_url else ""
        safe_imdb_url = escape(build_imdb_url(imdb_id))

        if not safe_poster_url:
            safe_poster_url = "https://via.placeholder.com/300x450?text=No+Poster"

        note_html = ""
        if safe_note:
            note_html = f'<div class="movie-note">{safe_note}</div>'

        flag_html = ""
        if safe_flag or safe_country:
            flag_html = (
                f'<div class="movie-country" title="{safe_country}">'
                f'<span class="movie-flag">{safe_flag}</span>'
                f'<span class="movie-country-name">{safe_country}</span>'
                f"</div>"
            )

        movie_cards.append(
            f"""
            <article class="movie-card" data-title="{safe_title.lower()}">
                <a
                    class="movie-poster-link"
                    href="{safe_imdb_url}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <div class="movie-poster-wrapper">
                        <img
                            class="movie-poster"
                            src="{safe_poster_url}"
                            alt="{safe_title}"
                        >
                        <div class="movie-rating">⭐ {safe_rating}</div>
                        {note_html}
                    </div>
                </a>

                <div class="movie-card-body">
                    <div class="movie-card-top">
                        <h2 class="movie-title">{safe_title}</h2>
                        {flag_html}
                    </div>
                    <div class="movie-meta">
                        <span class="movie-year">{safe_year}</span>
                        <span class="movie-rating-inline">IMDb {safe_rating}</span>
                    </div>
                </div>
            </article>
            """.strip()
        )

    return "\n".join(movie_cards)


def generate_website() -> None:
    """
    Generate a user-specific website from the template.
    """
    if not TEMPLATE_PATH.exists():
        print("Template file 'index_template.html' was not found.")
        return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
        template = file.read()

    movies = get_all_movies()
    movie_grid_html = build_movie_grid(movies)

    html_content = template.replace("__TEMPLATE_TITLE__", APP_TITLE)
    html_content = html_content.replace("__TEMPLATE_USER__", ACTIVE_USER["name"])
    html_content = html_content.replace("__TEMPLATE_COUNT__", str(len(movies)))
    html_content = html_content.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / f"{ACTIVE_USER['name']}.html"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"Website was generated successfully: {output_file.name}")


def command_switch_user() -> None:
    """
    Switch the active user profile.
    """
    global ACTIVE_USER
    ACTIVE_USER = select_user()


def execute_choice(choice: str) -> bool:
    """
    Execute the selected menu command.

    Args:
        choice: User menu choice.

    Returns:
        bool: False if the app should exit, otherwise True.
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
        "11": command_switch_user,
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
    global ACTIVE_USER

    ACTIVE_USER = select_user()
    should_continue = True

    while should_continue:
        print_menu()
        choice = input("Enter choice (0-11): ").strip()
        should_continue = execute_choice(choice)


if __name__ == "__main__":
    main()