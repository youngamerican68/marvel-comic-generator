"""
Jikan Anime API Client

A client for interacting with the Jikan API (MyAnimeList) to fetch random anime data.
Includes error handling and retry logic. No API key required!
"""
import time
import requests
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configuration constants
JIKAN_API_BASE_URL = "https://api.jikan.moe/v4"
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds (Jikan has rate limits, so we wait a bit longer)


class JikanAPIError(Exception):
    """Custom exception for Jikan API errors."""
    pass


class JikanClient:
    """A client for interacting with the Jikan API (MyAnimeList)."""

    def __init__(self):
        """
        Initialize the Jikan API client.

        Note: Jikan API does not require authentication!
        """
        self.base_url = JIKAN_API_BASE_URL
        self.headers = {
            'User-Agent': 'Cover Generator/1.0'
        }

    def get_random_anime(self) -> Tuple[Optional[int], Optional[Dict[str, Any]]]:
        """
        Fetch a single random anime from MyAnimeList via Jikan API.

        Returns:
            Tuple of (year, anime_data) where year is the release year
            and anime_data is None if no anime found

        Raises:
            JikanAPIError: If the API request fails after retries
        """
        # Send the request with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    f"{self.base_url}/random/anime",
                    headers=self.headers,
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()

                # Parse the response
                data = response.json()

                # Extract the anime data
                anime = data.get('data')
                if not anime:
                    logger.warning("No anime data in response")
                    return None, None

                # Extract year from the response
                year = anime.get('year')  # Jikan provides year directly
                if not year:
                    # Try to get it from aired.from date
                    aired = anime.get('aired', {})
                    if aired:
                        from_date = aired.get('from', '')
                        if from_date:
                            try:
                                year = int(from_date.split('-')[0])
                            except (ValueError, IndexError):
                                logger.debug(f"Could not parse year from aired.from: {from_date}")

                return year, anime

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise JikanAPIError("Request timed out after multiple attempts")

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code

                # Handle rate limiting (Jikan uses 429)
                if status_code == 429:
                    logger.warning(f"Rate limit hit (attempt {attempt + 1}/{MAX_RETRIES})")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * 2)  # Wait longer for rate limits
                        continue
                    raise JikanAPIError("Rate limit exceeded. Please wait before making more requests.")

                logger.error(f"HTTP error: {status_code}")
                raise JikanAPIError(f"Jikan API returned error: {status_code}")

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise JikanAPIError(f"Failed to connect to Jikan API: {str(e)}")

            except (KeyError, ValueError) as e:
                logger.error(f"Failed to parse API response: {str(e)}")
                raise JikanAPIError(f"Invalid API response format: {str(e)}")

        raise JikanAPIError("Unexpected error: maximum retries reached")


def main() -> None:
    """
    Main function for standalone script execution.
    Demonstrates fetching a random anime.
    """
    # Initialize Jikan client (no API key needed!)
    try:
        client = JikanClient()

        # Fetch a random anime
        year, anime = client.get_random_anime()
        if anime:
            # Extract anime details
            title = anime.get('title', 'Unknown')
            title_english = anime.get('title_english')

            # Use English title if available
            display_title = title_english if title_english else title

            # Get image URL (prefer large, fallback to smaller)
            images = anime.get('images', {})
            jpg_images = images.get('jpg', {})
            image_url = (
                jpg_images.get('large_image_url') or
                jpg_images.get('image_url') or
                'No image available'
            )

            print(f"Random Anime" + (f" from {year}" if year else "") + ":")
            print(f"Title: {display_title}")
            print(f"Cover URL: {image_url}")
            print(f"MyAnimeList: {anime.get('url', 'N/A')}")

            # Additional info
            if anime.get('synopsis'):
                synopsis = anime.get('synopsis', '')[:150]
                print(f"Synopsis: {synopsis}...")

        else:
            print("No anime found. Try again!")

    except JikanAPIError as e:
        print(f"Error fetching anime: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()
