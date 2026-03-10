"""
movie_storage_sql.py

Storage layer for the movie app using SQLite and SQLAlchemy.

This module is responsible for:
- creating the database and table if needed
- listing all movies
- adding a movie
- deleting a movie
- updating a movie rating
"""

from sqlalchemy import create_engine, text

# Database connection string for a local SQLite file.
DB_URL = "sqlite:///movies.db"

# Set echo=True while developing if you want to see SQL statements in the terminal.
engine = create_engine(DB_URL, echo=False)


def initialize_database() -> None:
    """
    Create the movies table if it does not already exist.
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


def list_movies() -> dict:
    """
    Retrieve all movies from the database.

    Returns:
        dict: A dictionary in this format:
            {
                "Inception": {"year": 2010, "rating": 8.8},
                "Interstellar": {"year": 2014, "rating": 8.6}
            }
    """
    query = text(
        """
        SELECT title, year, rating
        FROM movies
        ORDER BY title COLLATE NOCASE
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query)
        movies = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
        }
        for row in movies
    }


def add_movie(title: str, year: int, rating: float) -> None:
    """
    Add a new movie to the database.

    Args:
        title: The movie title
        year: The release year
        rating: The movie rating
    """
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
    """
    Delete a movie from the database by title.

    Args:
        title: The movie title to delete
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
            print(f"Movie '{title}' not found.")
        else:
            print(f"Movie '{title}' deleted successfully.")


def update_movie(title: str, rating: float) -> None:
    """
    Update the rating of a movie.

    Args:
        title: The movie title to update
        rating: The new rating
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
            print(f"Movie '{title}' not found.")
        else:
            print(f"Movie '{title}' updated successfully.")


# Initialize the database as soon as the module is imported.
initialize_database()