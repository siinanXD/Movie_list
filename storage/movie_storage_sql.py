"""SQLite storage layer for the movie app."""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

DATABASE_URL = "sqlite:///movies.db"
engine = create_engine(DATABASE_URL, echo=False)


def initialize_database() -> None:
    """Create tables if they do not exist and add missing columns."""
    create_users_table = text(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    )

    create_movies_table = text(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT DEFAULT '',
            note TEXT DEFAULT '',
            imdb_id TEXT DEFAULT '',
            country TEXT DEFAULT '',
            country_flag TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, title)
        )
        """
    )

    with engine.connect() as connection:
        connection.execute(create_users_table)
        connection.execute(create_movies_table)
        connection.commit()

    ensure_column_exists("movies", "poster_url", "TEXT DEFAULT ''")
    ensure_column_exists("movies", "note", "TEXT DEFAULT ''")
    ensure_column_exists("movies", "imdb_id", "TEXT DEFAULT ''")
    ensure_column_exists("movies", "country", "TEXT DEFAULT ''")
    ensure_column_exists("movies", "country_flag", "TEXT DEFAULT ''")


def ensure_column_exists(table_name: str, column_name: str, column_definition: str) -> None:
    """Add a column if it does not already exist."""
    pragma_query = text(f"PRAGMA table_info({table_name})")
    alter_query = text(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
    )

    with engine.connect() as connection:
        existing_columns = {
            row._mapping["name"]
            for row in connection.execute(pragma_query)
        }

        if column_name not in existing_columns:
            connection.execute(alter_query)
            connection.commit()


def list_users() -> list[dict]:
    """Return all users."""
    query = text("SELECT id, name FROM users ORDER BY name")

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    return [
        {
            "id": row._mapping["id"],
            "name": row._mapping["name"],
        }
        for row in rows
    ]


def add_user(name: str) -> int | None:
    """Add a user and return the new id, or None if it already exists."""
    query = text("INSERT INTO users (name) VALUES (:name)")

    try:
        with engine.connect() as connection:
            result = connection.execute(query, {"name": name})
            connection.commit()
            return result.lastrowid
    except IntegrityError:
        return None


def list_movies(user_id: int) -> dict:
    """Return all movies for a user as a nested dictionary."""
    query = text(
        """
        SELECT title, year, rating, poster_url, note, imdb_id, country, country_flag
        FROM movies
        WHERE user_id = :user_id
        ORDER BY title
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(query, {"user_id": user_id}).fetchall()

    movies = {}
    for row in rows:
        mapping = row._mapping
        movies[mapping["title"]] = {
            "year": mapping["year"],
            "rating": mapping["rating"],
            "poster_url": mapping["poster_url"] or "",
            "note": mapping["note"] or "",
            "imdb_id": mapping["imdb_id"] or "",
            "country": mapping["country"] or "",
            "country_flag": mapping["country_flag"] or "",
        }

    return movies


def add_movie(
    user_id: int,
    title: str,
    year: int,
    rating: float,
    poster_url: str = "",
    note: str = "",
    imdb_id: str = "",
    country: str = "",
    country_flag: str = "",
) -> bool:
    """Add a movie for a user."""
    query = text(
        """
        INSERT INTO movies (
            user_id, title, year, rating, poster_url, note, imdb_id, country, country_flag
        )
        VALUES (
            :user_id, :title, :year, :rating, :poster_url, :note, :imdb_id, :country, :country_flag
        )
        """
    )

    try:
        with engine.connect() as connection:
            connection.execute(
                query,
                {
                    "user_id": user_id,
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url,
                    "note": note,
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
    """Delete a movie by title."""
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


def update_movie(
    user_id: int,
    old_title: str,
    new_title: str,
    new_year: int,
    new_rating: float,
    new_note: str,
) -> bool:
    """Update a movie's editable fields."""
    query = text(
        """
        UPDATE movies
        SET title = :new_title,
            year = :new_year,
            rating = :new_rating,
            note = :new_note
        WHERE user_id = :user_id AND title = :old_title
        """
    )

    try:
        with engine.connect() as connection:
            result = connection.execute(
                query,
                {
                    "user_id": user_id,
                    "old_title": old_title,
                    "new_title": new_title,
                    "new_year": new_year,
                    "new_rating": new_rating,
                    "new_note": new_note,
                },
            )
            connection.commit()
        return result.rowcount > 0
    except IntegrityError:
        return False


def update_movie_country_flag(user_id: int, title: str, country_flag: str) -> bool:
    """Update the country flag for a specific movie."""
    query = text(
        """
        UPDATE movies
        SET country_flag = :country_flag
        WHERE user_id = :user_id AND title = :title
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "user_id": user_id,
                "title": title,
                "country_flag": country_flag,
            },
        )
        connection.commit()

    return result.rowcount > 0


def update_movie_metadata(
    user_id: int,
    title: str,
    imdb_id: str,
    country: str,
    country_flag: str,
    poster_url: str,
) -> bool:
    """Update stored metadata for an existing movie."""
    query = text(
        """
        UPDATE movies
        SET imdb_id = :imdb_id,
            country = :country,
            country_flag = :country_flag,
            poster_url = :poster_url
        WHERE user_id = :user_id AND title = :title
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "user_id": user_id,
                "title": title,
                "imdb_id": imdb_id,
                "country": country,
                "country_flag": country_flag,
                "poster_url": poster_url,
            },
        )
        connection.commit()

    return result.rowcount > 0