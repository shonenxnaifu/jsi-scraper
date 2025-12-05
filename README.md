# JSI Scraper

A web scraping project specifically designed to collect data from [jogjasonicindex.com](https://jogjasonicindex.com/) by parsing HTML elements.
Of course, this is ✨**vibe coded**✨ using [**QWEN CODE**](https://qwenlm.github.io/qwen-code-docs/en/). 

## Setup

1. Make sure you have Python 3.11+ installed (Python 3.10 is also supported when using Docker)
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Available Libraries

This project includes the following libraries specifically for scraping jogjasonicindex.com:
- `requests` - For making HTTP requests
- `beautifulsoup4` - For parsing HTML/XML
- `fastapi` - For API framework
- `uvicorn` - For ASGI server
- `pydantic` - For data validation

## Getting Started

The `scrape.py` file contains a basic template to start your scraping project for jogjasonicindex.com.

For API usage, see the main FastAPI application in `app/main.py`.

## API Usage

The project now includes a FastAPI application with two endpoints:

### Starting the API Server
```bash
cd app && uvicorn main:app --host 0.0.0.0 --port 8000
```

### Running with Docker
You can also run this application using Docker:

1. Build the Docker image:
```bash
docker build -t jsi-scraper .
```

2. Run the container:
```bash
docker run -p 8000:8000 jsi-scraper
```

The application will be available at `http://localhost:8000`.

### Endpoints

1. **JSON Endpoint**: `/scrape/json`
   - Method: GET
   - Parameters:
     - `max_pages` (optional): Limit the number of project pages to scrape
   - Returns: JSON formatted scraped data from jogjasonicindex.com

2. **CSV Endpoint**: `/scrape/csv`
   - Method: GET
   - Parameters:
     - `max_pages` (optional): Limit the number of project pages to scrape
   - Returns: CSV formatted scraped data from jogjasonicindex.com as a downloadable file

3. **JSON Range Endpoint**: `/scrape/json/range`
   - Method: GET
   - Parameters:
     - `page_from` (required): Starting page number (≥ 1)
     - `page_to` (required): Ending page number (≥ page_from)
   - Returns: JSON formatted scraped data from jogjasonicindex.com for the specified page range

4. **CSV Range Endpoint**: `/scrape/csv/range`
   - Method: GET
   - Parameters:
     - `page_from` (required): Starting page number (≥ 1)
     - `page_to` (required): Ending page number (≥ page_from)
   - Returns: CSV formatted scraped data from jogjasonicindex.com as a downloadable file for the specified page range

### API Documentation
After starting the server, visit `http://localhost:8000/docs` to access the interactive API documentation and test the endpoints.

## Important Notes

- Always respect [jogjasonicindex.com's](https://jogjasonicindex.com) `robots.txt` file
- Be mindful of rate limiting to avoid being blocked
- Check jogjasonicindex.com's terms of service before scraping
- This scraper is specifically designed for jogjasonicindex.com and may not work on other websites

## Improvements for Production Deployment

The application has been enhanced to handle production deployment challenges, specifically addressing 504 Gateway Timeout errors:

### Timeout Handling Improvements
1. **Request Timeout Protection**: Each HTTP request has a 30-second timeout with retry mechanism and exponential backoff
2. **Overall Scraping Timeout**: Total scraping operation limited to 60 seconds with automatic termination
3. **Improved Headers**: Better browser mimicry to reduce blocking chances
4. **Efficient Processing**: Reduced inter-request delay from 0.5s to 0.2s while maintaining server respectfulness

### Async Processing Implementation
1. **Thread Pool Executor**: Long-running scraping operations run in separate threads to prevent blocking
2. **Non-blocking Endpoints**: API endpoints use async/await patterns with thread pooling
3. **Graceful Shutdown**: Proper cleanup of thread pools on server shutdown

### Production Configuration
1. **Gunicorn Server**: Replaced simple uvicorn with Gunicorn for better production handling
2. **Configurable Workers**: Multiple worker processes for concurrent request handling
3. **Extended Timeouts**: Server timeout configuration increased to 300 seconds
4. **Enhanced Logging**: Better access and error logging for production monitoring

### Usage Recommendations
1. **Limit Scraping Scope**: Always specify `max_pages` parameter to prevent long-running operations
2. **Monitor Progress**: Check logs during operation to track scraping progress
3. **Implement Caching**: For repeated requests, consider implementing caching to reduce load
4. **Consider Background Jobs**: For extensive scraping, consider implementing a background job queue

## Releases

### Current Version
- Version: 1.0.0

### Release Process
This project follows semantic versioning. For information about releases and how to create them, see:
- [CHANGELOG.md](CHANGELOG.md) - Detailed changes for each release
- [RELEASE_NOTES.md](RELEASE_NOTES.md) - Detailed release notes

### Docker Images
Docker images are published to DockerHub with version tags. To use a specific version:
```bash
docker pull pawitrawarda/jsi-scraper:latest
```

### GitHub Releases
Check the [Releases](https://github.com/shonenxnaifu/jsi-scraper/releases) page for downloadable assets and release notes.
