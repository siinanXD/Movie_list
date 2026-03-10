"""
omdb_api.py

Handles communication with the OMDb API.
"""

import requests

API_KEY = "ffe2f1a1"
BASE_URL = "https://www.omdbapi.com/"


def fetch_movie(title: str) -> dict | None:
    """
    Fetch movie information from OMDb.

    Returns movie data or None.
    """
    params = {
        "apikey": API_KEY,
        "t": title,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        print("API is not accessible.")
        return None

    data = response.json()

    if data.get("Response") == "False":
        print("Movie not found.")
        return None

    return data