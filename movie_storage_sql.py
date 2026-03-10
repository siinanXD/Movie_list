"""
movie_storage_sql.py

SQL storage layer for the movie project.
Replaces the old JSON storage with SQLite using SQLAlchemy.

The API stays compatible with the previous movie_storage.py so that
movies.py does not need major changes.
"""

from sqlalchemy import create_engine, text

DB_URL = "sqlite:///movies.db"

engine = create_engine(DB_URL, echo=False)


def initialize_database() -> None:
    """Create the movies table if it does not exist."""
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


initialize_database()


def list_movies() -> dict:
    """
    Retrieve all movies from the database.

    Returns:
        dict: Movie dictionary in the same structure as the JSON version.
    """
    query = text(
        """
        SELECT title, year, rating
        FROM movies
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.fetchall()

    return {
        row[0]: {"year": row[1], "rating": row[2]}
        for row in rows
    }


# ---- Compatibility Layer ----
# Your movies.py still calls get_movies()
# so we map it to list_movies().


def get_movies() -> dict:
    """
    Compatibility wrapper for older code.

    movies.py still calls get_movies(), so we simply return list_movies().
    """
    return list_movies()


def add_movie(title: str, year: int, rating: float) -> None:
    """Add a movie to the database."""
    query = text(
        """
        INSERT INTO movies (title, year, rating)
        VALUES (:title, :year, :rating)
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
                },
            )
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except Exception as error:
            print(f"Error adding movie: {error}")


def delete_movie(title: str) -> None:
    """Delete a movie from the database."""
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
            print(f"Movie '{title}' not found.")
        else:
            print(f"Movie '{title}' deleted successfully.")


def update_movie(title: str, rating: float) -> None:
    """Update the rating of a movie."""
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
            print(f"Movie '{title}' not found.")
        else:
            print(f"Movie '{title}' updated successfully.")