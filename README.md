# Movie App

A Python CLI application for managing personal movie collections with multiple user profiles.

Each user has their own movie library, can add movies automatically via the OMDb API, write personal notes, and generate a responsive movie website with posters, ratings, IMDb links, and country flags.

---

## Features

- Multiple user profiles
- Separate movie collections for each user
- Add movies automatically using the OMDb API
- Store movie data in SQLite
- Add personal notes to movies
- Generate a user-specific website
- Display posters, ratings, and origin country flags
- Open IMDb page by clicking on the movie poster
- Responsive website layout for larger collections
- Search movies on the generated website

---

## Project Structure

```text
PythonProject3/
│
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── api/
│   ├── __init__.py
│   ├── omdb_api.py
│   └── country_flags_api.py
│
├── storage/
│   ├── __init__.py
│   └── movie_storage_sql.py
│
├── static/
│   ├── index_template.html
│   └── style.css
│
├── website/
│   └── <generated user websites>
│
└── data/
    └── movies.db