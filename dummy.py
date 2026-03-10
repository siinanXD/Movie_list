from movie_storage_sql import DB_PATH, add_movie, list_movies

print(DB_PATH)

add_movie("Interstellar", 2014, 8.7)
print(list_movies())
