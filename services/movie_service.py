"""Movie-related application services."""

from __future__ import annotations

import random

from api import country_flags_api, omdb_api
from cli.prompts import (
    prompt_float,
    prompt_int,
    prompt_non_empty_string,
    prompt_optional_string,
)
from storage import movie_storage_sql as storage


MovieDict = dict[str, dict]



def get_all_movies(user_id: int) -> MovieDict:
    """Return all movies for the given user."""
    return storage.list_movies(user_id)



def parse_year(year_text: str) -> int:
    """Parse the OMDb year field into an integer."""
    try:
        return int(year_text[:4])
    except (ValueError, TypeError):
        return 0



def parse_rating(rating_text: str) -> float:
    """Parse the OMDb rating field into a float."""
    try:
        if rating_text == "N/A":
            return 0.0
        return float(rating_text)
    except (ValueError, TypeError):
        return 0.0



def extract_primary_country(country_text: str) -> str:
    """Extract the first country from a comma-separated country string."""
    if not country_text:
        return ""
    return country_text.split(",")[0].strip()



def create_user() -> dict | None:
    """Create a new user profile through the CLI."""
    new_name = prompt_non_empty_string("Enter new user name: ")
    created_user = storage.create_user(new_name)

    if created_user is None:
        print("A user with that name already exists.")
        return None

    print(f"\nUser '{created_user['name']}' created successfully.")
    return created_user



def list_movies(user_id: int, user_name: str) -> None:
    """Display all movies for a user."""
    movies = get_all_movies(user_id)

    if not movies:
        print(f"{user_name}, your movie collection is empty.")
        return

    print(f"\n{len(movies)} movies in total:\n")

    for title, data in movies.items():
        note = data.get("note", "")
        country_flag = data.get("country_flag", "")
        country = data.get("country", "")
        rating = data.get("rating", 0.0)

        extras: list[str] = []
        if country_flag:
            extras.append(f"{country_flag} {country}".strip())
        extras.append(f"Rating: {rating}")

        info_line = " | ".join(extras)
        if note:
            print(f"{title} ({data['year']}): {info_line} | Note: {note}")
        else:
            print(f"{title} ({data['year']}): {info_line}")



def add_movie(user_id: int, user_name: str) -> None:
    """Fetch a movie via OMDb and add it to the database."""
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
        user_id=user_id,
        title=title,
        year=year,
        rating=rating,
        poster_url=poster_url,
        imdb_id=imdb_id,
        country=country,
        country_flag=country_flag,
    )

    if was_added:
        print(f"Movie '{title}' added to {user_name}'s collection!")
    else:
        print(f"Movie '{title}' already exists in {user_name}'s collection.")



def delete_movie(user_id: int) -> None:
    """Delete a movie from the database."""
    title = prompt_non_empty_string("Enter movie name to delete: ")
    was_deleted = storage.delete_movie(user_id, title)

    if was_deleted:
        print(f"Movie '{title}' deleted successfully.")
    else:
        print("Movie not found.")



def update_movie(user_id: int) -> None:
    """Update a movie's title, year, rating, and note."""
    current_title = prompt_non_empty_string("Enter movie name to update: ")
    movie = storage.get_movie_by_title(user_id=user_id, title=current_title)

    if movie is None:
        print("Movie not found.")
        return

    print("Leave a field empty to keep the current value.")

    new_title = prompt_optional_string(
        f"New title [{movie['title']}]: "
    ) or movie["title"]

    new_year = prompt_int(
        f"New year [{movie['year']}]: ",
        min_value=0,
        allow_empty=True,
    )
    if new_year is None:
        new_year = movie["year"]

    new_rating = prompt_float(
        f"New rating [{movie['rating']}]: ",
        min_value=0.0,
        max_value=10.0,
        allow_empty=True,
    )
    if new_rating is None:
        new_rating = movie["rating"]

    current_note = movie.get("note", "")
    note_placeholder = current_note if current_note else "empty"
    new_note_input = prompt_optional_string(f"New note [{note_placeholder}]: ")
    new_note = current_note if new_note_input == "" else new_note_input

    was_updated = storage.update_movie(
        user_id=user_id,
        current_title=current_title,
        new_title=new_title,
        new_year=new_year,
        new_rating=new_rating,
        new_note=new_note,
    )

    if was_updated:
        print(f"Movie '{current_title}' successfully updated.")
    else:
        print("Movie could not be updated. The new title may already exist.")



def show_random_movie(user_id: int, user_name: str) -> None:
    """Show a random movie from the collection."""
    movies = get_all_movies(user_id)

    if not movies:
        print(f"{user_name}, your movie collection is empty.")
        return

    title = random.choice(list(movies.keys()))
    data = movies[title]
    print(f"Your random movie: {title} ({data['year']}): {data['rating']}")



def search_movie(user_id: int, user_name: str) -> None:
    """Search the collection by partial movie title."""
    movies = get_all_movies(user_id)

    if not movies:
        print(f"{user_name}, your movie collection is empty.")
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



def show_movies_sorted_by_rating(user_id: int, user_name: str) -> None:
    """Display all movies sorted by rating in descending order."""
    movies = get_all_movies(user_id)

    if not movies:
        print(f"{user_name}, your movie collection is empty.")
        return

    sorted_movies = sorted(
        movies.items(),
        key=lambda item: item[1]["rating"],
        reverse=True,
    )

    print("\nMovies sorted by rating:\n")
    for title, data in sorted_movies:
        print(f"{title} ({data['year']}): {data['rating']}")



def filter_movies_by_minimum_rating(user_id: int, user_name: str) -> None:
    """Display all movies whose rating is above or equal to a threshold."""
    movies = get_all_movies(user_id)

    if not movies:
        print(f"{user_name}, your movie collection is empty.")
        return

    minimum_rating = prompt_float(
        "Enter minimum rating (0-10): ",
        min_value=0.0,
        max_value=10.0,
    )
    assert minimum_rating is not None

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
