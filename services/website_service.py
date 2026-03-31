"""Website generation services for movie collections."""

from __future__ import annotations

from html import escape
from pathlib import Path


MovieDict = dict[str, dict]



def build_imdb_url(imdb_id: str) -> str:
    """Build a clickable IMDb URL for a movie."""
    if not imdb_id:
        return "#"
    return f"https://www.imdb.com/title/{imdb_id}/"



def build_movie_card(title: str, data: dict) -> str:
    """Return the HTML card for a single movie."""
    year = data.get("year", "")
    rating = data.get("rating", 0.0)
    poster_url = data.get("poster_url", "")
    note = data.get("note", "")
    imdb_id = data.get("imdb_id", "")
    country = data.get("country", "")
    country_flag = data.get("country_flag", "")

    safe_title = escape(title)
    safe_year = escape(str(year))
    safe_rating = escape(f"{rating:.1f}")
    safe_note = escape(note)
    safe_country = escape(country)
    safe_flag = escape(country_flag)
    safe_poster_url = escape(poster_url) if poster_url else ""
    safe_imdb_url = escape(build_imdb_url(imdb_id))

    if not safe_poster_url:
        safe_poster_url = "https://via.placeholder.com/300x450?text=No+Poster"

    note_html = ""
    if safe_note:
        note_html = f'<div class="movie-note">{safe_note}</div>'

    flag_html = ""
    if safe_flag or safe_country:
        flag_html = (
            f'<div class="movie-country" title="{safe_country}">' 
            f'<span class="movie-flag">{safe_flag}</span>'
            f'<span class="movie-country-name">{safe_country}</span>'
            f"</div>"
        )

    return (
        f"""
        <article class="movie-card" data-title="{safe_title.lower()}">
            <a
                class="movie-poster-link"
                href="{safe_imdb_url}"
                target="_blank"
                rel="noopener noreferrer"
            >
                <div class="movie-poster-wrapper">
                    <img
                        class="movie-poster"
                        src="{safe_poster_url}"
                        alt="{safe_title}"
                    >
                    <div class="movie-rating">⭐ {safe_rating}</div>
                    {note_html}
                </div>
            </a>

            <div class="movie-card-body">
                <div class="movie-card-top">
                    <h2 class="movie-title">{safe_title}</h2>
                    {flag_html}
                </div>
                <div class="movie-meta">
                    <span class="movie-year">{safe_year}</span>
                    <span class="movie-rating-inline">IMDb {safe_rating}</span>
                </div>
            </div>
        </article>
        """.strip()
    )



def build_movie_grid(movies: MovieDict) -> str:
    """Build the HTML grid for all movies."""
    return "\n".join(build_movie_card(title, data) for title, data in movies.items())



def generate_website(
    app_title: str,
    template_path: Path,
    output_dir: Path,
    user: dict,
    movies: MovieDict,
) -> None:
    """Generate a user-specific movie website from the HTML template."""
    if not template_path.exists():
        print("Template file 'index_template.html' was not found.")
        return

    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()

    movie_grid_html = build_movie_grid(movies)

    html_content = template.replace("__TEMPLATE_TITLE__", app_title)
    html_content = html_content.replace("__TEMPLATE_USER__", user["name"])
    html_content = html_content.replace("__TEMPLATE_COUNT__", str(len(movies)))
    html_content = html_content.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{user['name']}.html"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"Website was generated successfully: {output_file.name}")
