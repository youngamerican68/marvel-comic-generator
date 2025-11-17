# Cover Generator - Comics & Anime

A web application that displays random comic book and anime covers using the Comic Vine API and Jikan (MyAnimeList) API. Built with Flask, featuring a responsive UI, dual-mode toggle, rate limiting, and comprehensive error handling.

**Toggle between Comic Mode and Anime Mode with a single switch!**

Discover:
- 📚 **Comics** from Marvel, DC, Image, Dark Horse, IDW, and hundreds more publishers
- 🎌 **Anime** from MyAnimeList's vast database of anime series and movies

## Features

- **Dual Mode Toggle**: Instantly switch between comics and anime with a sleek toggle switch
- **Random Discovery**: Browse random covers from either comics or anime
- **Comics Mode**: Access to 800,000+ comic issues from all publishers via Comic Vine API
- **Anime Mode**: Access to MyAnimeList's comprehensive anime database via Jikan API (NO API KEY NEEDED!)
- **Responsive Design**: Optimized for desktop and mobile devices
- **Rate Limiting**: Prevents API abuse with configurable limits
- **Error Handling**: Robust error handling with retry logic
- **Security**: HTTPS enforcement, CORS support, and secure API key management
- **Loading States**: Visual feedback with animated spinner
- **Dynamic Attribution**: Attribution updates based on current mode

## Prerequisites

- Python 3.7+
- **Optional**: Comic Vine API Key for comic mode ([get one here](https://comicvine.gamespot.com/api/))
- **Anime mode works without any API key!**

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

4. **Set up environment variables (Optional)**

   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```
   # Optional - only needed for comic mode
   COMIC_VINE_API_KEY=your_api_key_here

   LOG_LEVEL=INFO
   FLASK_ENV=development
   ```

   **Note**: If you don't set `COMIC_VINE_API_KEY`, the app will still work in anime-only mode!

5. **Run the application**
   ```bash
   python server.py
   ```

   The app will be available at `http://localhost:5000`

### Getting API Keys

#### Comic Vine (Optional - for Comic Mode)

1. Go to [https://comicvine.gamespot.com/api/](https://comicvine.gamespot.com/api/)
2. Sign up or log in with your GameSpot/Comic Vine account
3. Once logged in, your API key will be displayed
4. Copy the API key and add it to your `.env` file

**Rate Limit**: 200 requests per resource per hour

#### Jikan/MyAnimeList (Anime Mode - No Key Needed!)

Anime mode uses the free Jikan API which doesn't require any authentication. Just toggle to anime mode and start discovering!

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

3. **Set environment variables (optional)**
   ```bash
   # Only set if you want comic mode enabled
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

3. **Configure environment variables** (optional):
   - `COMIC_VINE_API_KEY` (only if you want comic mode)
   - `FLASK_ENV=production`
   - `LOG_LEVEL=WARNING`

4. **Deploy** using the `render.yaml` configuration

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COMIC_VINE_API_KEY` | **No** | - | Your Comic Vine API key (only needed for comic mode) |
| `FLASK_ENV` | No | `development` | Environment mode (`development` or `production`) |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `PORT` | No | `5000` | Port for the Flask server |

### Modes

#### Comic Mode
- Uses Comic Vine API
- Requires API key (free signup)
- 800,000+ comic issues
- Rate limit: 200 requests per hour

#### Anime Mode
- Uses Jikan API (MyAnimeList)
- **No API key required!**
- Comprehensive anime database
- Rate limit: ~60 requests per minute

### Rate Limiting

The application includes rate limiting to prevent API abuse:
- **Global limits**: 200 requests per day, 50 per hour
- **Random endpoint**: 1 request per second

For production deployments with multiple workers (Gunicorn), consider using Redis for rate limit storage.

## API Endpoints

### `GET /`
Serves the main HTML page with mode toggle.

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

### `GET /random-anime`
Fetches a random anime with a valid cover image.

**Response:**
```json
{
  "year": 2023,
  "comic": {
    "title": "Demon Slayer: Kimetsu no Yaiba",
    "coverUrl": "https://cdn.myanimelist.net/images/anime/.../l.jpg",
    "urls": [
      {
        "type": "detail",
        "url": "https://myanimelist.net/anime/..."
      }
    ]
  }
}
```

**Note**: The response key is `"comic"` for both modes for frontend compatibility.

### `GET /health`
Health check endpoint for monitoring.

## Project Structure

```
marvel-comic-generator/
├── public/              # Static frontend files
│   ├── index.html      # Main HTML page with toggle
│   ├── scripts.js      # Frontend JavaScript (mode switching)
│   └── styles.css      # CSS styles with toggle switch
├── server.py           # Flask application (dual-mode support)
├── comic_client.py     # Comic Vine API client
├── anime_client.py     # Jikan/MyAnimeList API client
├── random_comic.py     # (deprecated - kept for reference)
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku deployment config
├── render.yaml        # Render deployment config
├── .env.example       # Example environment variables
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## How It Works

### Comic Mode
1. Fetches random comics from Comic Vine's database using random offset
2. Validates cover image availability
3. Formats title from series name, issue number, and issue name
4. Retries up to 10 times if no valid image found

### Anime Mode
1. Uses Jikan API's `/random/anime` endpoint
2. Validates cover image availability
3. Prefers English titles when available
4. No API key authentication required!

## Security Considerations

1. **API keys optional** - Anime mode requires no keys
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** in production (automatically enforced)
4. **Rate limiting** prevents API abuse
5. **Error messages** don't expose sensitive information
6. **CORS** is configured for cross-origin requests

## Troubleshooting

### "Comic mode not available"

This means `COMIC_VINE_API_KEY` is not set. Either:
- Add your Comic Vine API key to `.env`
- Or just use anime mode (no key needed!)

### Anime mode works but comics don't

Make sure you've set `COMIC_VINE_API_KEY` in your `.env` file.

### Rate Limit Errors

**Comic Vine** (420): Wait for rate limit window to expire (200/hour limit)
**Jikan** (429): Wait 1-2 seconds between requests

### "No comic/anime found" messages

The app automatically retries up to 10 times. If you still see this, click "Randomize" again.

### Connection timeouts

Check your internet connection and API status. The app has built-in retry logic.

## API Attribution

### Comic Vine
- [Comic Vine API](https://comicvine.gamespot.com/api/)
- Comprehensive comic book database owned by Fandom/GameSpot
- All comic data and images © their respective publishers

### Jikan (MyAnimeList)
- [Jikan API](https://jikan.moe/)
- Unofficial MyAnimeList API
- All anime data courtesy of [MyAnimeList](https://myanimelist.net/)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational purposes. All comic and anime content are © their respective creators and publishers.

## Acknowledgments

- Comic data provided by [Comic Vine](https://comicvine.gamespot.com/) / Fandom
- Anime data provided by [MyAnimeList](https://myanimelist.net/) via [Jikan API](https://jikan.moe/)
- Built with [Flask](https://flask.palletsprojects.com/)

## What's New

### v3.0 - Dual Mode: Comics & Anime
- **Added Anime Mode** - Toggle between comics and anime!
- **Jikan API Integration** - Access MyAnimeList's anime database
- **No API Key for Anime** - Anime mode works without any authentication
- **Sleek Toggle Switch** - Modern UI for switching modes
- **Dynamic Attribution** - Updates based on current mode
- **Flexible Configuration** - Comic Vine API key is now optional
- All existing features maintained (security, error handling, etc.)

### v2.0 - Comic Vine Migration
- Switched from Marvel API to Comic Vine API
- Multi-publisher support for comics
- Enhanced comic title formatting

### v1.0 - Initial Release
- Marvel API support
- Comprehensive security improvements
- Rate limiting and error handling
