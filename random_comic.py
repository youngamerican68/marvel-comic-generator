import hashlib
import time
import random
import requests

class MarvelClient:
    """A client for interacting with the Marvel Comics API."""
    
    BASE_URL = "https://gateway.marvel.com/v1/public"
    
    def __init__(self, public_key: str, private_key: str):
        self.public_key = public_key
        self.private_key = private_key
    
    def _generate_auth_params(self):
        """Generate authentication parameters required for Marvel API requests."""
        ts = str(int(time.time()))
        hash_input = f"{ts}{self.private_key}{self.public_key}"
        hash_value = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        return {"ts": ts, "apikey": self.public_key, "hash": hash_value}
    
    def get_random_comic(self):
        """Fetch a single random comic from any year."""
        # Pick a random year between 1960 and 2023
        random_year = random.randint(1960, 2023)
        
        # Define the date range for the selected year
        start_date = f"{random_year}-01-01"
        end_date = f"{random_year}-12-31"
        
        # Generate Marvel API parameters
        params = self._generate_auth_params()
        params.update({
            "dateRange": f"{start_date},{end_date}",
            "limit": 1,  # Fetch only one comic
            "offset": random.randint(0, 100),  # Random offset for better randomization
            "orderBy": "onsaleDate",
            "format": "comic",
        })
        
        # Send the request to the Marvel API
        response = requests.get(f"{self.BASE_URL}/comics", params=params)
        response.raise_for_status()
        
        # Parse and return the comic data
        comics = response.json().get("data", {}).get("results", [])
        return random_year, comics[0] if comics else None

def main():
    # Your Marvel API keys
    PUBLIC_KEY = "fabd95acbc69b2a8bd1dac47b491bba9"
    PRIVATE_KEY = "e40ac2fcd4746d17684e9acee632fdc30b88d9a7"
    
    # Initialize Marvel client
    client = MarvelClient(PUBLIC_KEY, PRIVATE_KEY)
    
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

if __name__ == "__main__":
    main()


