# Marvel Comic Cover Generator

A web application that displays random Marvel comic covers using the Marvel Comics API. Built with Flask, featuring a responsive UI, rate limiting, and comprehensive error handling.

## Features

- **Random Comic Discovery**: Browse random Marvel comics from 1960-2023
- **Responsive Design**: Optimized for desktop and mobile devices
- **Rate Limiting**: Prevents API abuse with configurable limits
- **Error Handling**: Robust error handling with retry logic
- **Security**: HTTPS enforcement, CORS support, and secure API key management
- **Loading States**: Visual feedback with animated spinner
- **Marvel Attribution**: Proper attribution with links to Marvel resources

## Prerequisites

- Python 3.7+
- Marvel API Keys (get them from [Marvel Developer Portal](https://developer.marvel.com/))

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

   Edit `.env` and add your Marvel API keys:
   ```
   MARVEL_PUBLIC_KEY=your_public_key_here
   MARVEL_PRIVATE_KEY=your_private_key_here
   LOG_LEVEL=INFO
   FLASK_ENV=development
   ```

5. **Run the application**
   ```bash
   python server.py
   ```

   The app will be available at `http://localhost:5000`

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
   heroku config:set MARVEL_PUBLIC_KEY=your_public_key
   heroku config:set MARVEL_PRIVATE_KEY=your_private_key
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
   - `MARVEL_PUBLIC_KEY`
   - `MARVEL_PRIVATE_KEY`
   - `FLASK_ENV=production`
   - `LOG_LEVEL=WARNING`

4. **Deploy** using the `render.yaml` configuration

The application will automatically use the configuration from `render.yaml`.

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MARVEL_PUBLIC_KEY` | Yes | - | Your Marvel API public key |
| `MARVEL_PRIVATE_KEY` | Yes | - | Your Marvel API private key |
| `FLASK_ENV` | No | `development` | Environment mode (`development` or `production`) |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `PORT` | No | `5000` | Port for the Flask server |

### Rate Limiting

The application includes rate limiting to prevent API abuse:
- **Global limits**: 200 requests per day, 50 per hour
- **Random comic endpoint**: 1 request per second

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
Fetches a random Marvel comic with a valid cover image.

**Response:**
```json
{
  "year": 2015,
  "comic": {
    "title": "Amazing Spider-Man (2015) #1",
    "coverUrl": "http://i.annihil.us/u/prod/marvel/i/mg/.../detail.jpg",
    "urls": [
      {
        "type": "detail",
        "url": "http://marvel.com/comics/..."
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
├── random_comic.py     # Marvel API client
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
mypy server.py random_comic.py
```

## Security Considerations

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** in production (automatically enforced)
4. **Rate limiting** prevents API abuse
5. **Error messages** don't expose sensitive information
6. **CORS** is configured for cross-origin requests

## Troubleshooting

### "MARVEL_PUBLIC_KEY and MARVEL_PRIVATE_KEY environment variables are required"

Make sure you've created a `.env` file with your API keys, or set them as environment variables.

### Rate Limit Errors (429)

Wait for the rate limit window to expire, or adjust the limits in `server.py`.

### "No comic found" messages

The API occasionally returns comics without valid images. The app automatically retries up to 10 times to find a valid comic.

### Connection timeouts

Check your internet connection and Marvel API status. The app has built-in retry logic with 10-second timeouts.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational purposes. All Marvel characters and comics are © Marvel.

## Acknowledgments

- Data provided by [Marvel](http://marvel.com). © 2025 Marvel
- Built with [Flask](https://flask.palletsprojects.com/)
- Marvel API documentation: [developer.marvel.com](https://developer.marvel.com/)

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review [Marvel API Documentation](https://developer.marvel.com/docs)
- Open an issue in the repository
