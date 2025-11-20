# Todo List for Adding FastAPI to JSI Scrapper

## Current Stack Analysis
- Web scraping using `requests` and `BeautifulSoup4`
- Python-based project with multiple scraping libraries
- Currently a command-line script (`scrape.py`)
- Requirements include `requests`, `beautifulsoup4`, and other scraping libraries

## Category Page Structure (Based on category_page.html)
- The website is built on WordPress platform
- Category pages have pagination elements following the pattern: https://jogjasonicindex.com/category/projek (page 1), https://jogjasonicindex.com/category/projek/page/2/, etc.
- Category pages list project names with links to individual project pages
- HTML structure uses Gutenberg blocks and WordPress-specific elements
- The website includes a query-based post template that displays projects in a list
- Pagination controls are implemented using WordPress's built-in query pagination system
- Each project list item contains a title that links to the individual project page

## Project Page Structure (Based on projek_page.html)
- Project pages are individual WordPress posts with project-specific content
- Each project page contains the project name in the title tag
- Project details are likely contained within Gutenberg blocks or WordPress post content
- The pages include WordPress-specific elements like post titles, dates, and author information
- Project pages may contain structured data for the various fields we need to extract (nama projek (projek name/title), date_posted, author, deskripsi, format, anggota, genre, tahun, status, dikografi, pranala, tags, and media)
- HTML structure follows WordPress post format with content areas containing the detailed project information

## Scraping Flow
- Visit the main category page at https://jogjasonicindex.com/category/projek
- The category page contains pagination list of project names with links to the project pages
- Each category page follows the URL pattern: https://jogjasonicindex.com/category/projek for page 1, https://jogjasonicindex.com/category/projek/page/2/ for page 2, etc.
- Visit the category page first and get the URLs to the project pages through this page
- Iterate through all category pages until reaching the last page
- Visit each project page (web_sources/projek_page.html) and extract the detailed project data; here is the data that needs to be extracted:
  - **projek**: project name
  - **date_posted**: date posted / written by
  - **author**: article posted by
  - **deskripsi**: description of project
  - **format**: format group / solo
  - **anggota**: member of group / solo
  - **genre**: genre of the project
  - **tahun**: year of emergence
  - **status**: status of the project (aktif/bubar)
  - **diskografi**: discography of the project (table)
  - **pranala**: related link to the project (bandcamp, youtube, etc)
  - **tags**: related tags to the project
  - **media**: related images to the project

- Continue scraping all projects from all category pages until reaching the final page
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
- Modify function to handle pagination by scraping the static website at https://jogjasonicindex.com/category/projek and all its paginated pages to get project links until the last page
- Update function to visit each project page and extract detailed project data
- Handle errors appropriately for API context

### Task 4: Create JSON endpoint that returns scraped data in JSON format
- Design endpoint `/scrape/json` that scrapes the static website at https://jogjasonicindex.com/category/projek and all its paginated pages to get project links until the last page, then visits each project page
- Return scraped data from all project pages in structured JSON format
- Include proper error handling and validation for multi-page scraping

### Task 5: Create CSV endpoint that returns scraped data in CSV format
- Design endpoint `/scrape/csv` that scrapes the static website at https://jogjasonicindex.com/category/projek and all its paginated pages to get project links until the last page, then visits each project page
- Convert scraped data from all project pages to CSV format using Python's csv module
- Return as a downloadable CSV file response

### Task 6: Add Pydantic models for request/response validation if needed
- Define response models for structured data
- Use models in endpoint definitions for type hints

### Task 7: Implement CSV generation functionality using Python csv module
- Convert scraped data structures to CSV format
- Create proper headers and content formatting
- Handle special characters and encoding properly

### Task 8: Update requirements.txt with new dependencies
- Add `fastapi` and `uvicorn` to requirements.txt
- Ensure version compatibility with existing packages

### Task 9: Test both endpoints using FastAPI UI and command line
- Verify JSON endpoint scrapes the static website at https://jogjasonicindex.com/category/projek and all its paginated pages to get project links until the last page, then visits each project page and returns detailed data
  - Reference JSON response for one project:
  ```JSON
  {
    "projects": [
      {
        "nama_projek": "string",
        "date_posted": "string",
        "author": "string",
        "deskripsi": "string",
        "format": "string",
        "anggota": ["string_anggota1", "string_anggota2"],
        "genre": "string",
        "status": "string",
        "tahun": "string",
        "diskografi": [
          {
            "tahun": "string",
            "judul": "string",
            "jenis": "string",
            "format": "string",
            "pranala": ["string_url1", "string_url2"]
          }
        ],
        "pranala": ["string_url1", "string_url2"],
        "tags": ["string_tag1", "string_tag2"],
        "media": ["string_url1", "string_url2"]
      }
    ]
  }
  ```

- Verify CSV endpoint generates valid CSV files with detailed data from all project pages; CSV columns must match/align with JSON response
- Test the static website scraping functionality to ensure robustness for multi-page scraping

### Task 10: Implement pagination logic to navigate through all category pages
- Create function to follow the specific URL pattern: https://jogjasonicindex.com/category/projek (page 1), https://jogjasonicindex.com/category/projek/page/2/ (page 2), etc.
- Implement logic to detect the last category page and stop scraping
- Handle pagination elements in the HTML to move between category pages

### Task 11: Update README with API usage instructions
- Document the new API endpoints (no parameters needed as they target the static website)
- Include examples of how to use both JSON and CSV endpoints
- Add information about accessing the FastAPI UI
