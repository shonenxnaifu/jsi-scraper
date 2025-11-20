# JSI Scrapper

A web scraping project to collect data from websites by parsing HTML elements.

## Setup

1. Make sure you have Python 3.11 installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Available Libraries

This project includes the following web scraping libraries:
- `requests` - For making HTTP requests
- `beautifulsoup4` - For parsing HTML/XML
- `lxml` - For fast parsing with XPath support
- `selenium` - For browser automation
- `playwright` - For modern browser automation
- `scrapy` - For comprehensive scraping framework
- `pyquery` - For jQuery-like HTML manipulation

## Getting Started

Check the `web_scraping_libraries.md` file for detailed information about each library and recommendations on which to use for your specific project.

The `scrape.py` file contains a basic template to start your scraping project.

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
     - `url` (required): The category URL to scrape projects from
     - `max_pages` (optional): Limit the number of project pages to scrape
   - Returns: JSON formatted scraped data

2. **CSV Endpoint**: `/scrape/csv`
   - Method: GET
   - Parameters:
     - `url` (required): The category URL to scrape projects from
     - `max_pages` (optional): Limit the number of project pages to scrape
   - Returns: CSV formatted scraped data as a downloadable file

### API Documentation
After starting the server, visit `http://localhost:8000/docs` to access the interactive API documentation and test the endpoints.

## Important Notes

- Always respect the website's `robots.txt` file
- Be mindful of rate limiting to avoid being blocked
- Check the website's terms of service before scraping
- Consider using official APIs if available