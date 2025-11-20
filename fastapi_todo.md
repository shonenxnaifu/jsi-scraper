# Todo List for Adding FastAPI to JSI Scrapper

## Current Stack Analysis
- Web scraping using `requests` and `BeautifulSoup4`
- Python-based project with multiple scraping libraries
- Currently a command-line script (`scrape.py`)
- Requirements include `requests`, `beautifulsoup4`, and other scraping libraries

## Flow Scrapping
- visit page category, source page category in "web_sources/projek_page.html"
- each page contains projek name that has a link to the projek page, source projek page "web_sources/projek_page"
- each page contains page number and latest page number
- visit category page first and get the url to projek page through this page
- visit projek page and get the data's, here is the data that you need to be extracted
  - **projek**: project name
  - **date_posted**: date posted / written by
  - **author**: article posted by
  - **deskripsi**: description of project
  - **format**: format group / solo
  - **anggota**: member of group / solo
  - **genre**: genre of the project
  - **tahun**: year of emerge
  - **status**: status of the project (aktif/bubar)
  - **diskografi**: discography of the project (table)
  - **pranala**: related link to the project (bandcamp, youtube, etc)
  - **tags**: related tags to the project
  - **media**: related images to the project
 
- iterate until last page
## Implementation Plan

### Task 1: Install FastAPI and uvicorn dependencies
- Install `fastapi` and `uvicorn[standard]` packages
- Verify installation in virtual environment

### Task 2: Create a main FastAPI application file (main.py)
- Initialize FastAPI application instance
- Configure proper imports from current scraping module
- Set up basic route structure

### Task 3: Import and adapt the existing scrape_website function for API use
- Ensure the scraping function can be imported into the FastAPI app
- Modify function if needed to return structured data for API responses
- Handle errors appropriately for API context

### Task 4: Create JSON endpoint that returns scraped data in JSON format
- Design endpoint `/scrape/json` that accepts URL as parameter
- Return scraped data in structured JSON format
- Include proper error handling and validation

### Task 5: Create CSV endpoint that returns scraped data in CSV format
- Design endpoint `/scrape/csv` that accepts URL as parameter
- Convert scraped data to CSV format using Python's csv module
- Return as downloadable CSV file response

### Task 6: Add Pydantic models for request/response validation if needed
- Define request models for URL validation
- Create response models for structured data
- Use models in endpoint definitions for type hints

### Task 7: Implement CSV generation functionality using Python csv module
- Convert scraped data structures to CSV format
- Create proper headers and content formatting
- Handle special characters and encoding properly

### Task 8: Update requirements.txt with new dependencies
- Add `fastapi` and `uvicorn` to requirements.txt
- Ensure version compatibility with existing packages

### Task 9: Test both endpoints using FastAPI UI and command line
- Verify JSON endpoint returns proper JSON data
  - references JSON response:
  ```JSON
  {
    "nama_projek": "string"
    "date_posted": "string",
    "author": "string",
    "deskripsi": "string"
    "format": "string"
    "anggota": ["anggota1", "anggota2"]
    "genre": "string",
    "status": "string",
    "tahun": "string"
    "diskografi": [
      {
        "tahun": "string",
        "judul": "string",
        "jenis": "string",
        "format": "string",
        "pranala": ["url1", "url2"]
      }
      {
        "tahun": "string",
        "judul": "string",
        "jenis": "string",
        "format": "string",
        "pranala": ["url1", "url2"]
      }
    ],
    "pranala": "string",
    "tags": "media",
    "media": ["url1", "url2"]
  }
  ```

- Verify CSV endpoint generates valid CSV files
- Test with various URLs to ensure robustness

### Task 10: Update README with API usage instructions
- Document the new API endpoints and their parameters
- Include examples of how to use both JSON and CSV endpoints
- Add information about accessing the FastAPI UI
