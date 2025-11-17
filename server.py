"""
Comic & Anime Cover Generator Flask Application

A web application that displays random comic covers (Comic Vine API)
and anime covers (Jikan/MyAnimeList API).
Includes rate limiting, error handling, and security features.
"""
from flask import Flask, jsonify, send_from_directory, request, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import logging
import os
import sys
from typing import Dict, Optional, Tuple, Any
from dotenv import load_dotenv
from comic_client import ComicVineClient
from anime_client import JikanClient

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.static_folder = 'public'
app.static_url_path = '/static'

# Enable CORS if needed
CORS(app)

# Configure rate limiter
# Note: For production with multiple workers, use Redis storage:
# from flask_limiter.util import get_remote_address
# from limits.storage import RedisStorage
# limiter = Limiter(
#     app=app,
#     key_func=get_remote_address,
#     storage_uri="redis://localhost:6379",
#     default_limits=["200 per day", "50 per hour"]
# )
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Force HTTPS in production
@app.before_request
def force_https():
    """Redirect HTTP to HTTPS in production."""
    if os.environ.get('FLASK_ENV') == 'production':
        if not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)

# Get API key from environment variable (optional for anime-only mode)
COMIC_VINE_API_KEY = os.environ.get('COMIC_VINE_API_KEY')

# Initialize clients
comic_client = None
if COMIC_VINE_API_KEY:
    comic_client = ComicVineClient(COMIC_VINE_API_KEY)
    logger.info("Comic Vine client initialized")
else:
    logger.warning("COMIC_VINE_API_KEY not set - comic mode disabled")
    logger.warning("Get your API key from: https://comicvine.gamespot.com/api/")

# Initialize Jikan client (no API key needed!)
anime_client = JikanClient()
logger.info("Jikan anime client initialized")

# Configuration constants
MAX_RETRY_ATTEMPTS = 10


def is_valid_comic(comic: Dict[str, Any]) -> bool:
    """
    Check if a comic has valid image data.

    Args:
        comic: Comic data dictionary from Comic Vine API

    Returns:
        True if comic has valid image, False otherwise
    """
    if not comic:
        return False

    image = comic.get('image')
    if not image:
        return False

    # Check for any valid image URL (prefer medium, but accept others)
    medium_url = image.get('medium_url', '')
    small_url = image.get('small_url', '')
    original_url = image.get('original_url', '')

    return bool(medium_url or small_url or original_url)


def format_comic_response(comic: Dict[str, Any], year: Optional[int]) -> Dict[str, Any]:
    """
    Format comic data for API response.

    Args:
        comic: Raw comic data from Comic Vine API
        year: Year the comic was published (can be None)

    Returns:
        Formatted comic data dictionary
    """
    # Build the title from volume name, issue number, and issue name
    name = comic.get('name', '')
    issue_number = comic.get('issue_number', '')
    volume = comic.get('volume', {})
    volume_name = volume.get('name', 'Unknown Series') if volume else 'Unknown Series'

    # Format: "Series Name #123 - Issue Name" or variations
    if issue_number:
        title = f"{volume_name} #{issue_number}"
        if name:
            title += f" - {name}"
    else:
        title = volume_name
        if name:
            title += f" - {name}"

    # Get the best available image URL
    image = comic.get('image', {})
    cover_url = (
        image.get('medium_url') or
        image.get('small_url') or
        image.get('original_url') or
        ''
    )

    # Build URL for detail page
    detail_url = comic.get('site_detail_url', '')
    urls = []
    if detail_url:
        urls.append({
            'type': 'detail',
            'url': detail_url
        })

    comic_data = {
        "title": title,
        "coverUrl": cover_url,
        "urls": urls
    }

    response = {"comic": comic_data}
    if year:
        response["year"] = year

    return response


def is_valid_anime(anime: Dict[str, Any]) -> bool:
    """
    Check if an anime has valid image data.

    Args:
        anime: Anime data dictionary from Jikan API

    Returns:
        True if anime has valid image, False otherwise
    """
    if not anime:
        return False

    images = anime.get('images')
    if not images:
        return False

    jpg_images = images.get('jpg', {})
    return bool(jpg_images.get('large_image_url') or jpg_images.get('image_url'))


def format_anime_response(anime: Dict[str, Any], year: Optional[int]) -> Dict[str, Any]:
    """
    Format anime data for API response.

    Args:
        anime: Raw anime data from Jikan API
        year: Year the anime aired (can be None)

    Returns:
        Formatted anime data dictionary
    """
    # Get title (prefer English, fallback to romaji)
    title = anime.get('title_english') or anime.get('title') or 'Unknown Anime'

    # Get the best available image URL
    images = anime.get('images', {})
    jpg_images = images.get('jpg', {})
    cover_url = (
        jpg_images.get('large_image_url') or
        jpg_images.get('image_url') or
        ''
    )

    # Build URL for MyAnimeList page
    mal_url = anime.get('url', '')
    urls = []
    if mal_url:
        urls.append({
            'type': 'detail',
            'url': mal_url
        })

    anime_data = {
        "title": title,
        "coverUrl": cover_url,
        "urls": urls
    }

    response = {"comic": anime_data}  # Keep key as "comic" for frontend compatibility
    if year:
        response["year"] = year

    return response


@app.route('/')
def index() -> str:
    """Serve the main page."""
    return app.send_static_file('index.html')


@app.route('/random-comic')
@limiter.limit("1 per second")
def random_comic() -> Tuple[Dict[str, Any], int]:
    """
    Fetch and return a random comic with valid cover image.

    Returns:
        JSON response with comic data or error message
    """
    # Check if comic client is available
    if not comic_client:
        return jsonify({
            "error": "Comic mode not available",
            "message": "COMIC_VINE_API_KEY not configured. Get your API key from https://comicvine.gamespot.com/api/"
        }), 503

    attempt = 0

    try:
        while attempt < MAX_RETRY_ATTEMPTS:
            attempt += 1

            year, comic = comic_client.get_random_comic()

            if is_valid_comic(comic):
                # Build title for logging
                title = comic.get('name', 'Unknown')
                volume = comic.get('volume', {})
                if volume:
                    volume_name = volume.get('name', '')
                    if volume_name:
                        title = f"{volume_name} - {title}"

                logger.info(f"Found valid comic: {title}" + (f" from {year}" if year else ""))
                return jsonify(format_comic_response(comic, year)), 200

            if comic:
                logger.debug(f"Skipping comic with invalid image")
            else:
                logger.debug(f"No comic found at this offset")

        # Max attempts reached
        logger.warning(f"Could not find valid comic after {MAX_RETRY_ATTEMPTS} attempts")
        return jsonify({
            "error": "Could not find a comic with a valid cover image",
            "message": "Please try again"
        }), 404

    except Exception as e:
        # Log full error server-side, return generic message to client
        logger.error(f'Error fetching comic: {str(e)}', exc_info=True)
        return jsonify({
            "error": "Failed to fetch comic",
            "message": "An error occurred while fetching the comic. Please try again later."
        }), 500


@app.route('/random-anime')
@limiter.limit("1 per second")
def random_anime() -> Tuple[Dict[str, Any], int]:
    """
    Fetch and return a random anime with valid cover image.

    Returns:
        JSON response with anime data or error message
    """
    attempt = 0

    try:
        while attempt < MAX_RETRY_ATTEMPTS:
            attempt += 1

            year, anime = anime_client.get_random_anime()

            if is_valid_anime(anime):
                # Get title for logging
                title = anime.get('title_english') or anime.get('title', 'Unknown')

                logger.info(f"Found valid anime: {title}" + (f" from {year}" if year else ""))
                return jsonify(format_anime_response(anime, year)), 200

            if anime:
                logger.debug(f"Skipping anime with invalid image")
            else:
                logger.debug(f"No anime found")

        # Max attempts reached
        logger.warning(f"Could not find valid anime after {MAX_RETRY_ATTEMPTS} attempts")
        return jsonify({
            "error": "Could not find an anime with a valid cover image",
            "message": "Please try again"
        }), 404

    except Exception as e:
        # Log full error server-side, return generic message to client
        logger.error(f'Error fetching anime: {str(e)}', exc_info=True)
        return jsonify({
            "error": "Failed to fetch anime",
            "message": "An error occurred while fetching the anime. Please try again later."
        }), 500


@app.route('/health')
def health() -> Tuple[Dict[str, str], int]:
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
