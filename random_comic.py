"""
Marvel API Client

A client for interacting with the Marvel Comics API to fetch random comic data.
Includes authentication, error handling, and retry logic.
"""
import hashlib
import time
import random
import requests
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configuration constants
MARVEL_API_BASE_URL = "https://gateway.marvel.com/v1/public"
MIN_COMIC_YEAR = 1960
MAX_COMIC_YEAR = 2023
MAX_OFFSET = 100
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


class MarvelAPIError(Exception):
    """Custom exception for Marvel API errors."""
    pass


class MarvelClient:
    """A client for interacting with the Marvel Comics API."""

    def __init__(self, public_key: str, private_key: str):
        """
        Initialize the Marvel API client.

        Args:
            public_key: Marvel API public key
            private_key: Marvel API private key

        Raises:
            ValueError: If keys are empty or None
        """
        if not public_key or not private_key:
            raise ValueError("Public key and private key are required")

        self.public_key = public_key
        self.private_key = private_key
        self.base_url = MARVEL_API_BASE_URL

    def _generate_auth_params(self) -> Dict[str, str]:
        """
        Generate authentication parameters required for Marvel API requests.

        Returns:
            Dictionary containing timestamp, API key, and hash
        """
        ts = str(int(time.time()))
        hash_input = f"{ts}{self.private_key}{self.public_key}"
        hash_value = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        return {"ts": ts, "apikey": self.public_key, "hash": hash_value}

    def get_random_comic(self) -> Tuple[int, Optional[Dict[str, Any]]]:
        """
        Fetch a single random comic from a random year.

        Returns:
            Tuple of (year, comic_data) where comic_data is None if no comic found

        Raises:
            MarvelAPIError: If the API request fails after retries
        """
        # Pick a random year
        random_year = random.randint(MIN_COMIC_YEAR, MAX_COMIC_YEAR)

        # Define the date range for the selected year
        start_date = f"{random_year}-01-01"
        end_date = f"{random_year}-12-31"

        # Generate Marvel API parameters
        params = self._generate_auth_params()
        params.update({
            "dateRange": f"{start_date},{end_date}",
            "limit": 1,
            "offset": random.randint(0, MAX_OFFSET),
            "orderBy": "onsaleDate",
            "format": "comic",
        })

        # Send the request with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    f"{self.base_url}/comics",
                    params=params,
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()

                # Parse and return the comic data
                data = response.json()
                comics = data.get("data", {}).get("results", [])
                return random_year, comics[0] if comics else None

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise MarvelAPIError("Request timed out after multiple attempts")

            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise MarvelAPIError(f"Marvel API returned error: {e.response.status_code}")

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise MarvelAPIError(f"Failed to connect to Marvel API: {str(e)}")

            except (KeyError, ValueError) as e:
                logger.error(f"Failed to parse API response: {str(e)}")
                raise MarvelAPIError(f"Invalid API response format: {str(e)}")

        raise MarvelAPIError("Unexpected error: maximum retries reached")


def main() -> None:
    """
    Main function for standalone script execution.
    Demonstrates fetching a random comic.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Get API keys from environment
    public_key = os.environ.get('MARVEL_PUBLIC_KEY')
    private_key = os.environ.get('MARVEL_PRIVATE_KEY')

    if not public_key or not private_key:
        print("Error: MARVEL_PUBLIC_KEY and MARVEL_PRIVATE_KEY environment variables are required")
        print("Please set them in a .env file or as environment variables")
        return

    # Initialize Marvel client
    try:
        client = MarvelClient(public_key, private_key)

        # Fetch a random comic
        random_year, comic = client.get_random_comic()
        if comic:
            # Extract comic details
            title = comic.get("title", "Unknown Title")
            thumbnail = comic.get("thumbnail", {})
            image_url = f"{thumbnail.get('path')}/detail.{thumbnail.get('extension')}"

            print(f"Random Comic from {random_year}:")
            print(f"Title: {title}")
            print(f"Cover URL: {image_url}")
        else:
            print(f"No comics found for the year {random_year}.")

    except MarvelAPIError as e:
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
