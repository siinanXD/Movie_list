from movie_storage_sql import add_movie, delete_movie, list_movies, update_movie

add_movie("Inception", 2010, 8.8)
print(list_movies())

update_movie("Inception", 9.0)
print(list_movies())

delete_movie("Inception")
print(list_movies())