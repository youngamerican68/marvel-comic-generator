"""
Marvel Comic Generator Flask Application

A web application that displays random Marvel comic covers using the Marvel API.
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
from random_comic import MarvelClient

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

# Get API keys from environment variables (required)
PUBLIC_KEY = os.environ.get('MARVEL_PUBLIC_KEY')
PRIVATE_KEY = os.environ.get('MARVEL_PRIVATE_KEY')

if not PUBLIC_KEY or not PRIVATE_KEY:
    logger.error("MARVEL_PUBLIC_KEY and MARVEL_PRIVATE_KEY environment variables are required")
    sys.exit(1)

# Initialize Marvel API client
client = MarvelClient(PUBLIC_KEY, PRIVATE_KEY)

# Configuration constants
MAX_COMIC_RETRY_ATTEMPTS = 10


def is_valid_comic(comic: Dict[str, Any]) -> bool:
    """
    Check if a comic has valid thumbnail data.

    Args:
        comic: Comic data dictionary from Marvel API

    Returns:
        True if comic has valid thumbnail, False otherwise
    """
    if not comic:
        return False

    thumbnail = comic.get('thumbnail')
    if not thumbnail:
        return False

    path = thumbnail.get('path', '')
    extension = thumbnail.get('extension')

    return (path and extension and 'image_not_available' not in path)


def format_comic_response(comic: Dict[str, Any], year: int) -> Dict[str, Any]:
    """
    Format comic data for API response.

    Args:
        comic: Raw comic data from Marvel API
        year: Year the comic was published

    Returns:
        Formatted comic data dictionary
    """
    thumbnail = comic['thumbnail']
    comic_data = {
        "title": comic.get("title", "Unknown Title"),
        "coverUrl": f"{thumbnail['path']}/detail.{thumbnail['extension']}",
        "urls": comic.get("urls", [])
    }
    return {"year": year, "comic": comic_data}


@app.route('/')
def index() -> str:
    """Serve the main page."""
    return app.send_static_file('index.html')


@app.route('/random-comic')
@limiter.limit("1 per second")
def random_comic() -> Tuple[Dict[str, Any], int]:
    """
    Fetch and return a random Marvel comic with valid cover image.

    Returns:
        JSON response with comic data or error message
    """
    attempt = 0

    try:
        while attempt < MAX_COMIC_RETRY_ATTEMPTS:
            attempt += 1

            random_year, comic = client.get_random_comic()

            if is_valid_comic(comic):
                logger.info(f"Found valid comic: {comic.get('title')} from {random_year}")
                return jsonify(format_comic_response(comic, random_year)), 200

            if comic:
                logger.debug(f"Skipping comic with invalid image: {comic.get('title')}")
            else:
                logger.debug(f"No comic found for year {random_year}")

        # Max attempts reached
        logger.warning(f"Could not find valid comic after {MAX_COMIC_RETRY_ATTEMPTS} attempts")
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


@app.route('/health')
def health() -> Tuple[Dict[str, str], int]:
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
