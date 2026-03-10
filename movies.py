# movies.py
import random
import statistics

import matplotlib.pyplot as plt
from thefuzz import fuzz, process

import movie_storage_sql as movie_storage


CUTOFF_SCORE = 45


# ---------- UI / Input Helpers ----------

def menu():
    print("********** \033[33m My Movies Database \033[0m **********")

    menu_points = [
        "\033[32m Menu: \033[0m",
        "0. Exit",
        "1. List movies",
        "2. Add movie",
        "3. Delete movie",
        "4. Update movie",
        "5. Stats",
        "6. Random movie",
        "7. Search movie",
        "8. Movies sorted by rating",
        "9. Histogram",
        "10. Movies sorted by year",
        "11. Filter movies",
    ]
    for point in menu_points:
        print(point)


def prompt_non_empty_string(prompt: str) -> str:
    """Prompt until user enters a non-empty string."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("\033[31mInput cannot be empty. Please try again.\033[0m")


def prompt_int(prompt: str, allow_blank: bool = False):
    """Prompt for int; if allow_blank True, blank returns None."""
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("\033[31mPlease enter a valid integer.\033[0m")


def prompt_float(prompt: str, allow_blank: bool = False):
    """Prompt for float; accepts comma; if allow_blank True, blank returns None."""
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        raw = raw.replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            print("\033[31mPlease enter a valid number.\033[0m")


def prompt_rating() -> float:
    """Prompt until user enters a valid rating between 0 and 10."""
    while True:
        rating = prompt_float("Enter your movie rating (0-10): ")
        if 0 <= rating <= 10:
            return rating
        print("\033[31mRating must be between 0 and 10.\033[0m")


def prompt_newest_first() -> bool:
    """Returns True for newest-first, False for oldest-first."""
    while True:
        answer = input("Show newest movies first? (y/n): ").strip().lower()
        if answer in {"y", "yes", "j", "ja"}:
            return True
        if answer in {"n", "no", "nein"}:
            return False
        print("\033[31mPlease enter y or n.\033[0m")


# ---------- Menu Dispatcher ----------

def user_choice():
    choice = prompt_int("Enter your choice (0-11): ")
    print()

    actions = {
        0: exit_app,
        1: list_count_movies,
        2: add_movie,
        3: delete_movie,
        4: update_movie,
        5: stats,
        6: random_movie,
        7: search_movie,
        8: sorted_movies_by_rating,
        9: histogram,
        10: sorted_movies_by_year,
        11: filter_movies,
    }

    action = actions.get(choice)
    if action is None:
        print("\033[31m Invalid choice. Please try again! \033[0m")
        print()
        input("Press Enter to continue")
        return

    action()

    if choice != 0:
        print()
        input("Press Enter to continue")


def exit_app():
    print("Bye!")
    raise SystemExit


# ---------- Features ----------

def list_count_movies():
    movies = movie_storage.get_movies()
    print(f"{len(movies)} movies found")
    print()
    for title, data in movies.items():
        print(f"{title} ({data['year']}) - {data['rating']:.1f}")


def add_movie():
    movies = movie_storage.get_movies()

    title = prompt_non_empty_string("Enter your movie name: ")
    if title in movies:
        print(f"Movie {title} already exist!")
        return

    rating = prompt_rating()
    year = prompt_int("Enter year of release: ")

    movie_storage.add_movie(title, year, rating)
    print(f"Movie {title} successfully added")


def delete_movie():
    movies = movie_storage.get_movies()
    if not movies:
        print("No movies in the database.")
        return

    title = prompt_non_empty_string("Which movie do you want to delete? :")
    if title not in movies:
        print("Movie not found. Please try again.")
        return

    movie_storage.delete_movie(title)
    print("Your movie has been deleted")


def update_movie():
    movies = movie_storage.get_movies()
    if not movies:
        print("No movies in the database.")
        return

    title = prompt_non_empty_string("Enter your movie name: ")
    if title not in movies:
        print("Movie not found. Please try again.")
        return

    rating = prompt_rating()
    movie_storage.update_movie(title, rating)
    print("Your movie rating has been updated")


def stats():
    movies = movie_storage.get_movies()
    if not movies:
        print("No movies in the database.")
        return

    ratings = [data["rating"] for data in movies.values()]
    average_rating = sum(ratings) / len(ratings)
    median_rating = statistics.median(ratings)

    max_rating = max(ratings)
    min_rating = min(ratings)

    best_movies = [
        title for title, data in movies.items()
        if data["rating"] == max_rating
    ]
    worst_movies = [
        title for title, data in movies.items()
        if data["rating"] == min_rating
    ]

    print(f"Average Rating: {average_rating:.1f}")
    print(f"Median Rating: {median_rating:.1f}")

    print(f"Best Movie(s) ({max_rating:.1f}):")
    for title in best_movies:
        print(f"- {title} ({movies[title]['year']}) - {movies[title]['rating']:.1f}")

    print(f"Worst Movie(s) ({min_rating:.1f}):")
    for title in worst_movies:
        print(f"- {title} ({movies[title]['year']}) - {movies[title]['rating']:.1f}")



def random_movie():
    movies = movie_storage.get_movies()
    if not movies:
        print("No movies in the database.")
        return

    title = random.choice(list(movies.keys()))
    data = movies[title]
    print(f"Your movie for tonight is: {title} ({data['year']}) - {data['rating']:.1f}")


def search_movie():
    movies = movie_storage.get_movies()
    if not movies:
        print("No movies in the database.")
        return

    search_query = prompt_non_empty_string("Enter movie name or part of movie name: ")

    if search_query in movies:
        data = movies[search_query]
        print(f"\nExact match found: {search_query} ({data['year']}) - {data['rating']:.1f}")
        return

    q_lower = search_query.lower()
    contains_matches = [title for title in movies.keys() if q_lower in title.lower()]
    if contains_matches:
        print("\nMatches found:")
        for title in contains_matches:
            data = movies[title]
            print(f"- {title} ({data['year']}) - {data['rating']:.1f}")
        return

    matches = process.extract(
        search_query,
        movies.keys(),
        limit=5,
        scorer=fuzz.token_sort_ratio,
    )
    best_matches = [(title, score) for title, score in matches if score >= CUTOFF_SCORE]

    if best_matches:
        print(f'\nThe movie "{search_query}" does not exist. Did you mean:')
        for title, _score in best_matches:
            data = movies[title]
            print(f"- {title} ({data['year']}) - {data['rating']:.1f}")
    else:
        print(f'\nNo close matches found for "{search_query}".')


def sorted_movies_by_rating():
    movies = movie_storage.get_movies()
    if not movies:
        print("No movies in the database.")
        return

    sorted_movies = sorted(movies.items(), key=lambda item: item[1]["rating"], reverse=True)
    for title, data in sorted_movies:
        print(f"- {title} ({data['year']}) - {data['rating']:.1f}")


def sorted_movies_by_year():
    movies = movie_storage.get_movies()
    if not movies:
        print("No movies in the database.")
        return

    newest_first = prompt_newest_first()
    sorted_movies = sorted(movies.items(), key=lambda item: item[1]["year"], reverse=newest_first)

    for title, data in sorted_movies:
        print(f"- {title} ({data['year']}) - {data['rating']:.1f}")


def filter_movies():
    movies = movie_storage.get_movies()
    if not movies:
        print("No movies in the database.")
        return

    min_rating = prompt_float(
        "Enter minimum rating (leave blank for no minimum rating): ",
        allow_blank=True,
    )
    start_year = prompt_int(
        "Enter start year (leave blank for no start year): ",
        allow_blank=True,
    )
    end_year = prompt_int(
        "Enter end year (leave blank for no end year): ",
        allow_blank=True,
    )

    filtered = []
    for title, data in movies.items():
        rating = data["rating"]
        year = data["year"]

        if min_rating is not None and rating < min_rating:
            continue
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue

        filtered.append((title, year, rating))

    if not filtered:
        print("\nNo movies match the given criteria.")
        return

    print("\nFiltered Movies:")
    for title, year, rating in filtered:
        print(f"{title} ({year}): {rating:.1f}")


def histogram():
    movies = movie_storage.get_movies()
    if not movies:
        print("No movies in the database.")
        return

    ratings = [data["rating"] for data in movies.values()]
    plt.figure(figsize=(10, 6))
    plt.hist(ratings, bins=10, edgecolor="black", range=(0, 10))
    plt.title("Frequency Distribution of Movie Ratings")
    plt.xlabel("Rating (Points)")
    plt.ylabel("Number of Movies")
    plt.grid(axis="y", alpha=0.75)

    filename = "ratings_histogram.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Histogram saved as {filename}")


def main():
    while True:
        menu()
        print()
        user_choice()


if __name__ == "__main__":
    main()
