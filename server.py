from flask import Flask, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
from random_comic import MarvelClient

# Create Flask application
application = Flask(__name__)
app = application  # For Gunicorn compatibility

app.static_folder = 'public'
app.static_url_path = '/static'

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

PUBLIC_KEY = os.environ.get('MARVEL_PUBLIC_KEY', "fabd95acbc69b2a8bd1dac47b491bba9")
PRIVATE_KEY = os.environ.get('MARVEL_PRIVATE_KEY', "e40ac2fcd4746d17684e9acee632fdc30b88d9a7")
client = MarvelClient(PUBLIC_KEY, PRIVATE_KEY)

@app.route('/')
def index():
    logging.info('Serving index.html')
    return send_from_directory('public', 'index.html')

@app.route('/random-comic')
@limiter.limit("1 per second")
def random_comic():
    try:
        while True:
            random_year, comic = client.get_random_comic()
            if comic:
                if (comic.get('thumbnail') and 
                    comic['thumbnail'].get('path') and 
                    comic['thumbnail'].get('extension') and 
                    'image_not_available' not in comic['thumbnail']['path']):
                    
                    comic_data = {
                        "title": comic.get("title", "Unknown Title"),
                        "coverUrl": f"{comic['thumbnail']['path']}/detail.{comic['thumbnail']['extension']}",
                        "urls": comic.get("urls", [])
                    }
                    return jsonify({"year": random_year, "comic": comic_data})
                
                logging.info(f"Skipping comic with missing/invalid image: {comic.get('title')}")
                continue
            
            logging.warning(f"No comic found for year {random_year}")
            continue
            
    except Exception as e:
        logging.error(f'Error fetching comic: {str(e)}', exc_info=True)
        return jsonify({
            "error": "Failed to fetch comic",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)