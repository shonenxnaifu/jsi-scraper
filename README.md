# JSI Scraper

A web scraping project specifically designed to collect data from jogjasonicindex.com by parsing HTML elements.
Of course, this is ✨**vibe coded**✨ using [**QWEN CODE**](https://qwenlm.github.io/qwen-code-docs/en/). 

## Setup

1. Make sure you have Python 3.11 installed
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

Check the `web_scraping_libraries.md` file for detailed information about each library and recommendations on which to use for your specific project.

The `scrape.py` file contains a basic template to start your scraping project for jogjasonicindex.com.

For API usage, see the main FastAPI application in `main.py`.

## API Usage

The project now includes a FastAPI application with two endpoints:

### Starting the API Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

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

### API Documentation
After starting the server, visit `http://localhost:8000/docs` to access the interactive API documentation and test the endpoints.

## Important Notes

- Always respect jogjasonicindex.com's `robots.txt` file
- Be mindful of rate limiting to avoid being blocked
- Check jogjasonicindex.com's terms of service before scraping
- This scraper is specifically designed for jogjasonicindex.com and may not work on other websites
