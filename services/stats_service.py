"""Statistics-related services for movie collections."""

from __future__ import annotations

import statistics

from services.movie_service import get_all_movies


MovieDict = dict[str, dict]



def get_ratings(movies: MovieDict) -> list[float]:
    """Return a list of all movie ratings."""
    return [movie_data["rating"] for movie_data in movies.values()]



def get_average_rating(movies: MovieDict) -> float:
    """Return the average rating of the movie collection."""
    return statistics.mean(get_ratings(movies))



def get_median_rating(movies: MovieDict) -> float:
    """Return the median rating of the movie collection."""
    return statistics.median(get_ratings(movies))



def get_best_movie(movies: MovieDict) -> tuple[str, dict]:
    """Return the highest-rated movie."""
    return max(movies.items(), key=lambda item: item[1]["rating"])



def get_worst_movie(movies: MovieDict) -> tuple[str, dict]:
    """Return the lowest-rated movie."""
    return min(movies.items(), key=lambda item: item[1]["rating"])



def show_statistics(user_id: int, user_name: str) -> None:
    """Print collection statistics for a user."""
    movies = get_all_movies(user_id)

    if not movies:
        print(f"{user_name}, your movie collection is empty.")
        return

    average_rating = get_average_rating(movies)
    median_rating = get_median_rating(movies)
    best_movie = get_best_movie(movies)
    worst_movie = get_worst_movie(movies)

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
