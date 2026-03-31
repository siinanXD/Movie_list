"""Movie-related business logic."""

from __future__ import annotations

import random

from api import country_flags_api, omdb_api
from cli.prompts import prompt_float, prompt_int
from storage import movie_storage_sql as storage


def get_all_movies(user_id: int) -> dict:
    """Return all movies for a user."""
    return storage.list_movies(user_id)


def extract_primary_country(country_value: str) -> str:
    """Extract the first country from a comma-separated country string."""
    if not country_value:
        return ""
    return country_value.split(",")[0].strip()


def parse_year(year_value: str) -> int | None:
    """Parse a year string into an integer."""
    try:
        return int(year_value)
    except (TypeError, ValueError):
        return None


def parse_rating(rating_value: str) -> float | None:
    """Parse a rating string into a float."""
    try:
        return float(rating_value)
    except (TypeError, ValueError):
        return None


def list_movies(user_id: int, user_name: str) -> None:
    """Print all movies for the active user."""
    movies = get_all_movies(user_id)

    if not movies:
        print(f"\n{user_name} has no movies in the collection.")
        return

    print(f"\n{user_name}'s movies:")
    for index, (title, data) in enumerate(movies.items(), start=1):
        year = data.get("year", "N/A")
        rating = data.get("rating", "N/A")
        note = data.get("note", "")
        note_text = f" | Note: {note}" if note else ""
        print(f"{index}. {title} ({year}) - Rating: {rating}{note_text}")

    print(f"Total movies: {len(movies)}")


def add_movie(user_id: int, user_name: str) -> None:
    """Add a movie via OMDb data."""
    title = input("Enter movie title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    existing_movies = get_all_movies(user_id)
    if title in existing_movies:
        print(f"Movie '{title}' already exists in {user_name}'s collection.")
        return

    api_data = omdb_api.fetch_movie(title)
    if api_data is None:
        print("Movie not found or API error occurred.")
        return

    movie_title = api_data.get("Title", title).strip()
    movie_year = parse_year(api_data.get("Year", ""))
    movie_rating = parse_rating(api_data.get("imdbRating", ""))
    movie_imdb_id = api_data.get("imdbID", "") or ""
    movie_country = extract_primary_country(api_data.get("Country", ""))
    movie_country_flag = (
        country_flags_api.fetch_flag(movie_country) if movie_country else ""
    )
    poster_url = api_data.get("Poster", "") or ""

    if poster_url == "N/A":
        poster_url = ""

    if movie_year is None:
        movie_year = prompt_int("Enter release year manually: ", 1800, 2100)

    if movie_rating is None:
        movie_rating = prompt_float("Enter rating manually: ", 0.0, 10.0)

    success = storage.add_movie(
        user_id=user_id,
        title=movie_title,
        year=movie_year,
        rating=movie_rating,
        poster_url=poster_url,
        note="",
        imdb_id=movie_imdb_id,
        country=movie_country,
        country_flag=movie_country_flag,
    )

    if success:
        print(f"Movie '{movie_title}' added to {user_name}'s collection.")
    else:
        print("Could not add movie.")


def delete_movie(user_id: int) -> None:
    """Delete a movie by title."""
    title = input("Enter movie title to delete: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    deleted = storage.delete_movie(user_id, title)
    if deleted:
        print(f"Movie '{title}' deleted.")
    else:
        print(f"Movie '{title}' not found.")


def update_movie(user_id: int) -> None:
    """Update a movie's title, year, rating, and note."""
    movies = get_all_movies(user_id)
    if not movies:
        print("No movies available.")
        return

    old_title = input("Enter movie title to update: ").strip()
    if old_title not in movies:
        print(f"Movie '{old_title}' not found.")
        return

    movie_data = movies[old_title]

    print("Leave input empty to keep the current value.")

    new_title = input(f"New title [{old_title}]: ").strip() or old_title

    year_input = input(f"New year [{movie_data.get('year', '')}]: ").strip()
    if year_input:
        parsed_year = parse_year(year_input)
        if parsed_year is None:
            print("Invalid year.")
            return
        new_year = parsed_year
    else:
        new_year = movie_data.get("year", 0)

    rating_input = input(f"New rating [{movie_data.get('rating', '')}]: ").strip()
    if rating_input:
        parsed_rating = parse_rating(rating_input)
        if parsed_rating is None or not 0 <= parsed_rating <= 10:
            print("Invalid rating. It must be between 0 and 10.")
            return
        new_rating = parsed_rating
    else:
        new_rating = movie_data.get("rating", 0.0)

    current_note = movie_data.get("note", "")
    new_note = input(f"New note [{current_note}]: ").strip()
    if not new_note:
        new_note = current_note

    updated = storage.update_movie(
        user_id=user_id,
        old_title=old_title,
        new_title=new_title,
        new_year=new_year,
        new_rating=new_rating,
        new_note=new_note,
    )

    if not updated:
        print("Movie could not be updated.")
        return

    if new_title != old_title or not movie_data.get("imdb_id") or not movie_data.get("country_flag"):
        refresh_movie_metadata(user_id, new_title)

    print(f"Movie '{old_title}' updated.")


def show_random_movie(user_id: int, user_name: str) -> None:
    """Show one random movie."""
    movies = get_all_movies(user_id)
    if not movies:
        print(f"\n{user_name} has no movies in the collection.")
        return

    title, data = random.choice(list(movies.items()))
    print("\nRandom movie:")
    print(f"{title} ({data.get('year', 'N/A')}) - Rating: {data.get('rating', 'N/A')}")


def search_movie(user_id: int, user_name: str) -> None:
    """Search movies by title substring."""
    query = input("Enter search term: ").strip().lower()
    if not query:
        print("Search term cannot be empty.")
        return

    movies = get_all_movies(user_id)
    matches = {
        title: data
        for title, data in movies.items()
        if query in title.lower()
    }

    if not matches:
        print(f"No matches found in {user_name}'s collection.")
        return

    print(f"\nSearch results for '{query}':")
    for title, data in matches.items():
        print(f"- {title} ({data.get('year', 'N/A')}) - Rating: {data.get('rating', 'N/A')}")


def show_movies_sorted_by_rating(user_id: int, user_name: str) -> None:
    """Print movies sorted by rating descending."""
    movies = get_all_movies(user_id)
    if not movies:
        print(f"\n{user_name} has no movies in the collection.")
        return

    sorted_movies = sorted(
        movies.items(),
        key=lambda item: item[1].get("rating", 0),
        reverse=True,
    )

    print("\nMovies sorted by rating:")
    for index, (title, data) in enumerate(sorted_movies, start=1):
        print(f"{index}. {title} - Rating: {data.get('rating', 'N/A')}")


def filter_movies_by_minimum_rating(user_id: int, user_name: str) -> None:
    """Show movies with a rating greater than or equal to a threshold."""
    minimum_rating = prompt_float("Enter minimum rating: ", 0.0, 10.0)
    movies = get_all_movies(user_id)

    filtered_movies = {
        title: data
        for title, data in movies.items()
        if data.get("rating", 0) >= minimum_rating
    }

    if not filtered_movies:
        print(f"No movies with rating >= {minimum_rating} found for {user_name}.")
        return

    print(f"\nMovies with rating >= {minimum_rating}:")
    for title, data in filtered_movies.items():
        print(f"- {title} ({data.get('year', 'N/A')}) - Rating: {data.get('rating', 'N/A')}")


def refresh_movie_metadata(user_id: int, title: str) -> None:
    """Refresh metadata for one movie from OMDb."""
    api_data = omdb_api.fetch_movie(title)
    if api_data is None:
        return

    imdb_id = api_data.get("imdbID", "") or ""
    country = extract_primary_country(api_data.get("Country", ""))
    country_flag = country_flags_api.fetch_flag(country) if country else ""
    poster_url = api_data.get("Poster", "") or ""

    if poster_url == "N/A":
        poster_url = ""

    storage.update_movie_metadata(
        user_id=user_id,
        title=title,
        imdb_id=imdb_id,
        country=country,
        country_flag=country_flag,
        poster_url=poster_url,
    )


def backfill_missing_movie_metadata(user_id: int) -> None:
    """Fetch and store missing metadata for older movie entries."""
    movies = get_all_movies(user_id)

    for title, data in movies.items():
        imdb_id = data.get("imdb_id", "")
        country_flag = data.get("country_flag", "")
        poster_url = data.get("poster_url", "")
        country = data.get("country", "")

        if imdb_id and country_flag and poster_url:
            continue

        api_data = omdb_api.fetch_movie(title)
        if api_data is None:
            continue

        fetched_imdb_id = api_data.get("imdbID", "") or imdb_id
        fetched_country = extract_primary_country(api_data.get("Country", "")) or country
        fetched_country_flag = (
            country_flags_api.fetch_flag(fetched_country) if fetched_country else country_flag
        )
        fetched_poster_url = api_data.get("Poster", "") or poster_url

        if fetched_poster_url == "N/A":
            fetched_poster_url = ""

        storage.update_movie_metadata(
            user_id=user_id,
            title=title,
            imdb_id=fetched_imdb_id,
            country=fetched_country,
            country_flag=fetched_country_flag,
            poster_url=fetched_poster_url,
        )