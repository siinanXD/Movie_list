"""
movie_storage_sql.py

SQLite storage layer using SQLAlchemy.
Stores movies with title, year, rating and poster URL.
"""

from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "movies.db"
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo=False)


def initialize_database() -> None:
    """
    Create the movies table if it does not exist and make sure the
    poster_url column exists in older databases.
    """
    create_table_query = text(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL
        )
        """
    )

    with engine.connect() as connection:
        connection.execute(create_table_query)
        connection.commit()

    ensure_poster_url_column()


def ensure_poster_url_column() -> None:
    """
    Add the poster_url column if it does not already exist.

    This keeps older databases compatible with the new schema.
    """
    pragma_query = text("PRAGMA table_info(movies)")
    alter_query = text(
        """
        ALTER TABLE movies
        ADD COLUMN poster_url TEXT
        """
    )

    with engine.connect() as connection:
        result = connection.execute(pragma_query)
        columns = [row[1] for row in result.fetchall()]

        if "poster_url" not in columns:
            connection.execute(alter_query)
            connection.commit()


def list_movies() -> dict:
    """
    Return all movies from the database.

    Returns:
        dict: Movies in the following format:
            {
                "Inception": {
                    "year": 2010,
                    "rating": 8.8,
                    "poster_url": "https://..."
                }
            }
    """
    query = text(
        """
        SELECT title, year, rating, poster_url
        FROM movies
        ORDER BY title COLLATE NOCASE
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
            "poster_url": row[3] or "",
        }
        for row in rows
    }


def get_movies() -> dict:
    """
    Compatibility wrapper for older code.

    Returns:
        dict: All movies from the database.
    """
    return list_movies()


def add_movie(title: str, year: int, rating: float, poster_url: str = "") -> None:
    """
    Add a movie to the database.

    Args:
        title: Movie title.
        year: Release year.
        rating: IMDb rating.
        poster_url: Poster image URL.
    """
    query = text(
        """
        INSERT INTO movies (title, year, rating, poster_url)
        VALUES (:title, :year, :rating, :poster_url)
        """
    )

    with engine.connect() as connection:
        try:
            connection.execute(
                query,
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url,
                },
            )
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except IntegrityError:
            print(f"Movie '{title}' already exists.")


def delete_movie(title: str) -> None:
    """
    Delete a movie from the database.

    Args:
        title: Movie title.
    """
    query = text(
        """
        DELETE FROM movies
        WHERE title = :title
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"title": title})
        connection.commit()

        if result.rowcount == 0:
            print("Movie not found.")
        else:
            print(f"Movie '{title}' deleted successfully.")


def update_movie(title: str, rating: float) -> None:
    """
    Update the rating of a movie.

    Args:
        title: Movie title.
        rating: New rating.
    """
    query = text(
        """
        UPDATE movies
        SET rating = :rating
        WHERE title = :title
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "title": title,
                "rating": rating,
            },
        )
        connection.commit()

        if result.rowcount == 0:
            print("Movie not found.")
        else:
            print(f"Movie '{title}' updated successfully.")


initialize_database()