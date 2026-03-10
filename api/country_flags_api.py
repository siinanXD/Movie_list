"""
country_flags_api.py

Fetches country flag emojis from the REST Countries API.
"""

from typing import Any

import requests

BASE_URL = "https://restcountries.com/v3.1/name"


COUNTRY_ALIASES = {
    "USA": "United States",
    "US": "United States",
    "UK": "United Kingdom",
    "U.K.": "United Kingdom",
    "South Korea": "Korea",
    "North Korea": "Korea",
    "Russia": "Russian Federation",
}


def normalize_country_name(country_name: str) -> str:
    """
    Normalize common country aliases to improve API matching.

    Args:
        country_name: Raw country name.

    Returns:
        str: Normalized country name.
    """
    cleaned = country_name.strip()
    return COUNTRY_ALIASES.get(cleaned, cleaned)


def fetch_flag(country_name: str) -> str:
    """
    Fetch a country flag emoji from REST Countries.

    Args:
        country_name: Country name.

    Returns:
        str: Emoji flag if found, otherwise empty string.
    """
    if not country_name.strip():
        return ""

    normalized_name = normalize_country_name(country_name)

    params = {
        "fields": "flag",
        "fullText": "true",
    }

    try:
        response = requests.get(
            f"{BASE_URL}/{normalized_name}",
            params=params,
            timeout=10,
        )

        if response.status_code == 404:
            response = requests.get(
                f"{BASE_URL}/{normalized_name}",
                params={"fields": "flag"},
                timeout=10,
            )

        response.raise_for_status()
    except requests.exceptions.RequestException:
        return ""

    data: list[dict[str, Any]] = response.json()

    if not data:
        return ""

    return data[0].get("flag", "")