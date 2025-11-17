"""
Comic Vine API Client

A client for interacting with the Comic Vine API to fetch random comic data.
Includes authentication, error handling, and retry logic.
"""
import time
import random
import requests
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configuration constants
COMIC_VINE_API_BASE_URL = "https://comicvine.gamespot.com/api"
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Comic Vine has ~800k issues, but we'll use a conservative estimate
# for random offset to ensure we get results
MAX_RANDOM_OFFSET = 100000


class ComicVineAPIError(Exception):
    """Custom exception for Comic Vine API errors."""
    pass


class ComicVineClient:
    """A client for interacting with the Comic Vine API."""

    def __init__(self, api_key: str):
        """
        Initialize the Comic Vine API client.

        Args:
            api_key: Comic Vine API key

        Raises:
            ValueError: If API key is empty or None
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = COMIC_VINE_API_BASE_URL
        self.headers = {
            'User-Agent': 'Comic Cover Generator/1.0'
        }

    def get_random_comic(self) -> Tuple[Optional[int], Optional[Dict[str, Any]]]:
        """
        Fetch a single random comic issue.

        Returns:
            Tuple of (year, comic_data) where year is extracted from cover_date
            and comic_data is None if no comic found

        Raises:
            ComicVineAPIError: If the API request fails after retries
        """
        # Use a random offset to get random comics
        random_offset = random.randint(0, MAX_RANDOM_OFFSET)

        # Build request parameters
        params = {
            'api_key': self.api_key,
            'format': 'json',
            'limit': 1,
            'offset': random_offset,
            'field_list': 'id,name,issue_number,volume,cover_date,image,site_detail_url'
        }

        # Send the request with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    f"{self.base_url}/issues/",
                    params=params,
                    headers=self.headers,
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()

                # Parse the response
                data = response.json()

                # Check API-level errors
                if data.get('error') != 'OK':
                    error_msg = data.get('error', 'Unknown error')
                    logger.error(f"Comic Vine API error: {error_msg}")
                    raise ComicVineAPIError(f"API returned error: {error_msg}")

                # Extract results
                results = data.get('results', [])
                if not results:
                    logger.warning(f"No results found at offset {random_offset}")
                    return None, None

                comic = results[0]

                # Extract year from cover_date (format: YYYY-MM-DD)
                cover_date = comic.get('cover_date', '')
                year = None
                if cover_date:
                    try:
                        year = int(cover_date.split('-')[0])
                    except (ValueError, IndexError):
                        logger.warning(f"Could not parse year from cover_date: {cover_date}")

                return year, comic

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise ComicVineAPIError("Request timed out after multiple attempts")

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code

                # Handle rate limiting
                if status_code == 420:
                    logger.error("Rate limit exceeded (420)")
                    raise ComicVineAPIError("Rate limit exceeded. Please wait before making more requests.")

                logger.error(f"HTTP error: {status_code}")
                raise ComicVineAPIError(f"Comic Vine API returned error: {status_code}")

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise ComicVineAPIError(f"Failed to connect to Comic Vine API: {str(e)}")

            except (KeyError, ValueError) as e:
                logger.error(f"Failed to parse API response: {str(e)}")
                raise ComicVineAPIError(f"Invalid API response format: {str(e)}")

        raise ComicVineAPIError("Unexpected error: maximum retries reached")


def main() -> None:
    """
    Main function for standalone script execution.
    Demonstrates fetching a random comic.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Get API key from environment
    api_key = os.environ.get('COMIC_VINE_API_KEY')

    if not api_key:
        print("Error: COMIC_VINE_API_KEY environment variable is required")
        print("Get your API key from: https://comicvine.gamespot.com/api/")
        return

    # Initialize Comic Vine client
    try:
        client = ComicVineClient(api_key)

        # Fetch a random comic
        year, comic = client.get_random_comic()
        if comic:
            # Extract comic details
            name = comic.get('name', 'Unknown')
            issue_number = comic.get('issue_number', '')
            volume = comic.get('volume', {})
            volume_name = volume.get('name', 'Unknown Series') if volume else 'Unknown Series'

            # Build title
            if issue_number:
                title = f"{volume_name} #{issue_number}"
                if name:
                    title += f" - {name}"
            else:
                title = f"{volume_name}" + (f" - {name}" if name else "")

            # Get image URL
            image = comic.get('image', {})
            image_url = image.get('medium_url') or image.get('small_url') or 'No image available'

            print(f"Random Comic" + (f" from {year}" if year else "") + ":")
            print(f"Title: {title}")
            print(f"Cover URL: {image_url}")
            print(f"Details: {comic.get('site_detail_url', 'N/A')}")
        else:
            print("No comic found. Try again!")

    except ComicVineAPIError as e:
        print(f"Error fetching comic: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()
