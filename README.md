# Comic Cover Generator

A web application that displays random comic book covers from all publishers using the Comic Vine API. Built with Flask, featuring a responsive UI, rate limiting, and comprehensive error handling.

Discover covers from Marvel, DC Comics, Image, Dark Horse, and many more publishers!

## Features

- **Random Comic Discovery**: Browse random comic covers from across the entire comic book industry
- **All Publishers**: Not just Marvel - includes DC, Image, Dark Horse, IDW, and hundreds more
- **Responsive Design**: Optimized for desktop and mobile devices
- **Rate Limiting**: Prevents API abuse with configurable limits
- **Error Handling**: Robust error handling with retry logic
- **Security**: HTTPS enforcement, CORS support, and secure API key management
- **Loading States**: Visual feedback with animated spinner
- **Proper Attribution**: Links to Comic Vine for detailed information

## Prerequisites

- Python 3.7+
- Comic Vine API Key (get one from [Comic Vine API](https://comicvine.gamespot.com/api/))

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd marvel-comic-generator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Comic Vine API key:
   ```
   COMIC_VINE_API_KEY=your_api_key_here
   LOG_LEVEL=INFO
   FLASK_ENV=development
   ```

5. **Run the application**
   ```bash
   python server.py
   ```

   The app will be available at `http://localhost:5000`

### Getting a Comic Vine API Key

1. Go to [https://comicvine.gamespot.com/api/](https://comicvine.gamespot.com/api/)
2. Sign up or log in with your GameSpot/Comic Vine account
3. Once logged in, your API key will be displayed
4. Copy the API key and add it to your `.env` file

**Note**: Comic Vine API has a rate limit of 200 requests per resource per hour.

### Production Deployment

#### Heroku

1. **Install Heroku CLI and login**
   ```bash
   heroku login
   ```

2. **Create a new Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**
   ```bash
   heroku config:set COMIC_VINE_API_KEY=your_api_key
   heroku config:set FLASK_ENV=production
   heroku config:set LOG_LEVEL=WARNING
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

#### Render

1. **Create account on [Render](https://render.com/)**

2. **Connect your repository**

3. **Configure environment variables** in the Render dashboard:
   - `COMIC_VINE_API_KEY`
   - `FLASK_ENV=production`
   - `LOG_LEVEL=WARNING`

4. **Deploy** using the `render.yaml` configuration

The application will automatically use the configuration from `render.yaml`.

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COMIC_VINE_API_KEY` | Yes | - | Your Comic Vine API key |
| `FLASK_ENV` | No | `development` | Environment mode (`development` or `production`) |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `PORT` | No | `5000` | Port for the Flask server |

### Rate Limiting

The application includes rate limiting to prevent API abuse:
- **Global limits**: 200 requests per day, 50 per hour
- **Random comic endpoint**: 1 request per second

**Important**: Comic Vine's API allows 200 requests per resource per hour. The application is configured to stay well within these limits.

For production deployments with multiple workers (Gunicorn), consider using Redis for rate limit storage:

```python
# Uncomment in server.py
from limits.storage import RedisStorage
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200 per day", "50 per hour"]
)
```

## API Endpoints

### `GET /`
Serves the main HTML page.

### `GET /random-comic`
Fetches a random comic with a valid cover image.

**Response:**
```json
{
  "year": 2015,
  "comic": {
    "title": "The Amazing Spider-Man #1 - Lucky to Be Alive",
    "coverUrl": "https://comicvine.gamespot.com/a/uploads/.../medium.jpg",
    "urls": [
      {
        "type": "detail",
        "url": "https://comicvine.gamespot.com/..."
      }
    ]
  }
}
```

**Error Response:**
```json
{
  "error": "Failed to fetch comic",
  "message": "An error occurred while fetching the comic. Please try again later."
}
```

### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

## Project Structure

```
marvel-comic-generator/
├── public/              # Static frontend files
│   ├── index.html      # Main HTML page
│   ├── scripts.js      # Frontend JavaScript
│   └── styles.css      # CSS styles
├── server.py           # Flask application
├── comic_client.py     # Comic Vine API client
├── random_comic.py     # (deprecated - kept for reference)
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku deployment config
├── render.yaml        # Render deployment config
├── .env.example       # Example environment variables
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Style

The project follows PEP 8 guidelines. Use tools like `black` and `flake8`:

```bash
pip install black flake8
black .
flake8 .
```

### Type Checking

Type hints are included throughout. Use `mypy` for type checking:

```bash
pip install mypy
mypy server.py comic_client.py
```

## How It Works

1. **Random Selection**: The app uses a random offset to fetch comics from Comic Vine's database of 800,000+ issues
2. **Image Validation**: Each comic is checked to ensure it has a valid cover image
3. **Retry Logic**: If a comic doesn't have a valid image, the app tries again (up to 10 attempts)
4. **Title Formatting**: Combines series name, issue number, and issue name for display
5. **Best Image**: Selects the best available image quality (medium preferred)

## Security Considerations

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** in production (automatically enforced)
4. **Rate limiting** prevents API abuse and respects Comic Vine's limits
5. **Error messages** don't expose sensitive information
6. **CORS** is configured for cross-origin requests

## Troubleshooting

### "COMIC_VINE_API_KEY environment variable is required"

Make sure you've created a `.env` file with your API key, or set it as an environment variable.

### Rate Limit Errors (420)

Comic Vine limits to 200 requests per resource per hour. Wait for the rate limit window to expire, or adjust usage patterns.

### "No comic found" messages

The API occasionally returns offsets with no results. The app automatically retries up to 10 times to find a valid comic.

### Connection timeouts

Check your internet connection and Comic Vine API status. The app has built-in retry logic with 10-second timeouts.

### Missing images or broken image links

Some comics in the database don't have cover images. The app filters these out, but if you see a broken image, click "Randomize" again.

## API Attribution

This application uses the [Comic Vine API](https://comicvine.gamespot.com/api/).

**Comic Vine** is a comprehensive comic book database owned by Fandom/GameSpot that provides data on:
- Comic book issues, volumes, and series
- Characters, creators, and publishers
- Cover images and detailed metadata

All comic data and images are © their respective publishers and creators.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational purposes. All comic book characters, covers, and related content are © their respective publishers and creators.

## Acknowledgments

- Data provided by [Comic Vine](https://comicvine.gamespot.com/) / Fandom
- Built with [Flask](https://flask.palletsprojects.com/)
- Comic Vine API documentation: [comicvine.gamespot.com/api](https://comicvine.gamespot.com/api/)

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review [Comic Vine API Documentation](https://comicvine.gamespot.com/api/documentation)
- Open an issue in the repository

## What's New

### v2.0 - Comic Vine Migration
- **Switched from Marvel API to Comic Vine API** - Marvel API is no longer accessible
- **Multi-publisher support** - Now displays comics from Marvel, DC, Image, Dark Horse, and hundreds more
- **Enhanced comic title formatting** - Better display of series name, issue number, and title
- **Improved image selection** - Uses best available image quality
- All security and code quality improvements from v1.0 maintained
