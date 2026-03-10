"""
movie_storage_sql.py

SQLite storage layer using SQLAlchemy.
Supports multiple users, where each user has their own movie collection.
Each movie can also store a personal note, IMDb id, and origin country data.
"""

from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "movies.db"
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo=False)


def initialize_database() -> None:
    """
    Create the required database tables if they do not exist and
    make sure older databases are migrated to the current schema.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    create_users_table_query = text(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """
    )

    create_movies_table_query = text(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT,
            note TEXT,
            imdb_id TEXT,
            country TEXT,
            country_flag TEXT,
            UNIQUE(user_id, title),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    with engine.connect() as connection:
        connection.execute(create_users_table_query)
        connection.execute(create_movies_table_query)
        connection.commit()

    ensure_movies_table_columns()


def ensure_movies_table_columns() -> None:
    """
    Add missing columns to older databases if necessary.
    """
    pragma_query = text("PRAGMA table_info(movies)")

    with engine.connect() as connection:
        result = connection.execute(pragma_query)
        columns = [row[1] for row in result.fetchall()]

        if "poster_url" not in columns:
            connection.execute(text("ALTER TABLE movies ADD COLUMN poster_url TEXT"))
            connection.commit()

        if "note" not in columns:
            connection.execute(text("ALTER TABLE movies ADD COLUMN note TEXT"))
            connection.commit()

        if "imdb_id" not in columns:
            connection.execute(text("ALTER TABLE movies ADD COLUMN imdb_id TEXT"))
            connection.commit()

        if "country" not in columns:
            connection.execute(text("ALTER TABLE movies ADD COLUMN country TEXT"))
            connection.commit()

        if "country_flag" not in columns:
            connection.execute(text("ALTER TABLE movies ADD COLUMN country_flag TEXT"))
            connection.commit()


def list_users() -> list[dict]:
    """
    Return all users ordered by name.

    Returns:
        list[dict]: Example:
            [{"id": 1, "name": "John"}, {"id": 2, "name": "Sara"}]
    """
    query = text(
        """
        SELECT id, name
        FROM users
        ORDER BY name COLLATE NOCASE
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.fetchall()

    return [{"id": row[0], "name": row[1]} for row in rows]


def create_user(name: str) -> dict | None:
    """
    Create a new user.

    Args:
        name: Name of the user.

    Returns:
        dict | None: The created user or None if the name already exists.
    """
    insert_query = text(
        """
        INSERT INTO users (name)
        VALUES (:name)
        """
    )

    select_query = text(
        """
        SELECT id, name
        FROM users
        WHERE name = :name
        """
    )

    with engine.connect() as connection:
        try:
            connection.execute(insert_query, {"name": name})
            connection.commit()
        except IntegrityError:
            return None

        result = connection.execute(select_query, {"name": name})
        row = result.fetchone()

    if row is None:
        return None

    return {"id": row[0], "name": row[1]}


def list_movies(user_id: int) -> dict:
    """
    Return all movies for a specific user.

    Args:
        user_id: ID of the active user.

    Returns:
        dict: Movies for the selected user.
    """
    query = text(
        """
        SELECT title, year, rating, poster_url, note, imdb_id, country, country_flag
        FROM movies
        WHERE user_id = :user_id
        ORDER BY title COLLATE NOCASE
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"user_id": user_id})
        rows = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
            "poster_url": row[3] or "",
            "note": row[4] or "",
            "imdb_id": row[5] or "",
            "country": row[6] or "",
            "country_flag": row[7] or "",
        }
        for row in rows
    }


def add_movie(
    user_id: int,
    title: str,
    year: int,
    rating: float,
    poster_url: str = "",
    imdb_id: str = "",
    country: str = "",
    country_flag: str = "",
) -> bool:
    """
    Add a movie for a specific user.

    Args:
        user_id: ID of the active user.
        title: Movie title.
        year: Release year.
        rating: IMDb rating.
        poster_url: Poster image URL.
        imdb_id: IMDb identifier.
        country: Origin country.
        country_flag: Emoji flag of the origin country.

    Returns:
        bool: True if added successfully, otherwise False.
    """
    query = text(
        """
        INSERT INTO movies (
            user_id,
            title,
            year,
            rating,
            poster_url,
            note,
            imdb_id,
            country,
            country_flag
        )
        VALUES (
            :user_id,
            :title,
            :year,
            :rating,
            :poster_url,
            :note,
            :imdb_id,
            :country,
            :country_flag
        )
        """
    )

    with engine.connect() as connection:
        try:
            connection.execute(
                query,
                {
                    "user_id": user_id,
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url,
                    "note": "",
                    "imdb_id": imdb_id,
                    "country": country,
                    "country_flag": country_flag,
                },
            )
            connection.commit()
            return True
        except IntegrityError:
            return False


def delete_movie(user_id: int, title: str) -> bool:
    """
    Delete a movie for a specific user.

    Args:
        user_id: ID of the active user.
        title: Movie title.

    Returns:
        bool: True if deleted, otherwise False.
    """
    query = text(
        """
        DELETE FROM movies
        WHERE user_id = :user_id AND title = :title
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "user_id": user_id,
                "title": title,
            },
        )
        connection.commit()

    return result.rowcount > 0


def update_movie_note(user_id: int, title: str, note: str) -> bool:
    """
    Update the personal note of a movie for a specific user.

    Args:
        user_id: ID of the active user.
        title: Movie title.
        note: Personal note for the movie.

    Returns:
        bool: True if updated, otherwise False.
    """
    query = text(
        """
        UPDATE movies
        SET note = :note
        WHERE user_id = :user_id AND title = :title
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "user_id": user_id,
                "title": title,
                "note": note,
            },
        )
        connection.commit()

    return result.rowcount > 0


initialize_database()