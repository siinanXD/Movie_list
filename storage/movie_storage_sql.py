"""SQLite storage layer using SQLAlchemy for movie collections."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "movies.db"
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo=False)



def initialize_database() -> None:
    """Create tables and ensure the database schema is up to date."""
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
    """Add missing columns to older movie tables when necessary."""
    pragma_query = text("PRAGMA table_info(movies)")

    with engine.connect() as connection:
        result = connection.execute(pragma_query)
        columns = [row[1] for row in result.fetchall()]

        missing_columns = {
            "poster_url": "ALTER TABLE movies ADD COLUMN poster_url TEXT",
            "note": "ALTER TABLE movies ADD COLUMN note TEXT",
            "imdb_id": "ALTER TABLE movies ADD COLUMN imdb_id TEXT",
            "country": "ALTER TABLE movies ADD COLUMN country TEXT",
            "country_flag": "ALTER TABLE movies ADD COLUMN country_flag TEXT",
        }

        for column_name, alter_query in missing_columns.items():
            if column_name not in columns:
                connection.execute(text(alter_query))
                connection.commit()



def list_users() -> list[dict]:
    """Return all users ordered by name."""
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
    """Create a new user or return None when the name already exists."""
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
    """Return all movies for a specific user."""
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



def get_movie_by_title(user_id: int, title: str) -> dict | None:
    """Return a single movie record for a user by title."""
    query = text(
        """
        SELECT title, year, rating, poster_url, note, imdb_id, country, country_flag
        FROM movies
        WHERE user_id = :user_id AND title = :title
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"user_id": user_id, "title": title})
        row = result.fetchone()

    if row is None:
        return None

    return {
        "title": row[0],
        "year": row[1],
        "rating": row[2],
        "poster_url": row[3] or "",
        "note": row[4] or "",
        "imdb_id": row[5] or "",
        "country": row[6] or "",
        "country_flag": row[7] or "",
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
    """Add a movie for a specific user."""
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
    """Delete a movie for a specific user."""
    query = text(
        """
        DELETE FROM movies
        WHERE user_id = :user_id AND title = :title
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"user_id": user_id, "title": title})
        connection.commit()

    return result.rowcount > 0



def update_movie(
    user_id: int,
    current_title: str,
    new_title: str,
    new_year: int,
    new_rating: float,
    new_note: str,
) -> bool:
    """Update a movie's editable fields for a specific user."""
    query = text(
        """
        UPDATE movies
        SET title = :new_title,
            year = :new_year,
            rating = :new_rating,
            note = :new_note
        WHERE user_id = :user_id AND title = :current_title
        """
    )

    with engine.connect() as connection:
        try:
            result = connection.execute(
                query,
                {
                    "user_id": user_id,
                    "current_title": current_title,
                    "new_title": new_title,
                    "new_year": new_year,
                    "new_rating": new_rating,
                    "new_note": new_note,
                },
            )
            connection.commit()
        except IntegrityError:
            return False

    return result.rowcount > 0



def update_movie_note(user_id: int, title: str, note: str) -> bool:
    """Update only the note of a movie for backward compatibility."""
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
