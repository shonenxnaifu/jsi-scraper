from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import csv
import logging

from scraper import scrape_all_projects
from models import ScrapeResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="JSI Scraper API",
    description="API for scraping project data from jogjasonicindex.com",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "JSI Scraper API", "description": "API for scraping project data from jogjasonicindex.com"}


@app.get("/scrape/json", response_model=ScrapeResponse)
async def scrape_json(
    max_pages: Optional[int] = Query(None, description="Limit the number of project pages to scrape")
):
    """
    Scrape project data from jogjasonicindex.com and return as JSON
    """
    try:
        logger.info("Starting JSON scraping process...")
        projects = scrape_all_projects(max_pages=max_pages)
        logger.info(f"Scraping completed. Total projects: {len(projects)}")
        
        response = ScrapeResponse(projects=projects)
        return response
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


def flatten_project_data(projects):
    """
    Flatten project data for CSV generation, handling nested structures like discography
    """
    flattened_projects = []

    for project in projects:
        # Create a base project with flattened fields
        flat_project = {
            'nama_projek': project.get('nama_projek', ''),
            'date_posted': project.get('date_posted', ''),
            'author': project.get('author', ''),
            'deskripsi': project.get('deskripsi', ''),
            'format': project.get('format', ''),
            'anggota': ', '.join(project.get('anggota', [])),
            'genre': project.get('genre', ''),
            'tahun': project.get('tahun', ''),
            'status': project.get('status', ''),
            'pranala': ', '.join(project.get('pranala', [])),
            'tags': ', '.join(project.get('tags', [])),
            'media': ', '.join(project.get('media', []))
        }

        # Handle discography - since it's an array, we'll flatten it as a JSON string representation
        diskografi_list = project.get('diskografi', [])
        if diskografi_list:
            diskografi_strs = []
            for disk in diskografi_list:
                disk_str = f"{disk.get('tahun', '')}|{disk.get('judul', '')}|{disk.get('jenis', '')}|{disk.get('format', '')}|{', '.join(disk.get('pranala', []))}"
                diskografi_strs.append(disk_str)
            flat_project['diskografi'] = ';;'.join(diskografi_strs)  # Use ;; as separator between albums
        else:
            flat_project['diskografi'] = ''

        flattened_projects.append(flat_project)

    return flattened_projects

def generate_csv_content(projects):
    """
    Generate CSV content from project data
    """
    if not projects:
        return ""

    # Flatten project data for CSV
    flattened_projects = flatten_project_data(projects)

    # Define the CSV headers based on the expected data fields
    headers = [
        'nama_projek', 'date_posted', 'author', 'deskripsi', 'format',
        'anggota', 'genre', 'tahun', 'status', 'diskografi', 'pranala',
        'tags', 'media'
    ]

    # Create a string buffer to hold CSV content
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)

    # Write the header
    writer.writeheader()

    # Write each project as a row
    for project in flattened_projects:
        # Ensure all required keys exist
        row = {header: project.get(header, '') for header in headers}
        writer.writerow(row)

    # Get the content and close the buffer
    content = output.getvalue()
    output.close()

    return content

@app.get("/scrape/csv")
async def scrape_csv(
    max_pages: Optional[int] = Query(None, description="Limit the number of project pages to scrape")
):
    """
    Scrape project data from jogjasonicindex.com and return as CSV file
    """
    try:
        logger.info("Starting CSV scraping process...")
        projects = scrape_all_projects(max_pages=max_pages)
        logger.info(f"Scraping completed. Total projects: {len(projects)}")

        # Generate CSV content
        csv_content = generate_csv_content(projects)

        # Create a streaming response for the CSV content
        response = StreamingResponse(io.StringIO(csv_content), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=jogjasonicindex_projects.csv"
        return response
    except Exception as e:
        logger.error(f"Error during CSV scraping: {e}")
        raise HTTPException(status_code=500, detail=f"CSV scraping failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "JSI Scraper API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
