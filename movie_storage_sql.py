"""
movie_storage_sql.py

SQLite storage layer using SQLAlchemy.
Stores movies with title, year, rating and poster URL.
"""

from pathlib import Path

from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "movies.db"

DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo=False)


def initialize_database() -> None:
    """Create movies table if it does not exist."""
    create_table_query = text(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT
        )
        """
    )

    with engine.connect() as connection:
        connection.execute(create_table_query)
        connection.commit()


initialize_database()


def list_movies() -> dict:
    """Return all movies."""
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
            "poster_url": row[3],
        }
        for row in rows
    }


def add_movie(title: str, year: int, rating: float, poster_url: str) -> None:
    """Add a movie."""
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
        except Exception:
            print(f"Movie '{title}' already exists.")


def delete_movie(title: str) -> None:
    """Delete a movie."""
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
    """Update rating."""
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