from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import csv
import logging

from .scraper import scrape_all_projects, scrape_page_range
from .models import ScrapeResponse
from .__version__ import __version__
from .state_manager import state_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="JSI Scraper API",
    description="API for scraping project data from jogjasonicindex.com",
    version=__version__
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
    # Check if scraping is already in progress
    if state_manager.is_scraping():
        raise HTTPException(status_code=423, detail="Scraping process is currently in progress. Please wait until it completes or check status at /scrape/status")

    try:
        logger.info("Starting JSON scraping process...")
        state_manager.start_scraping()

        def progress_callback(progress, total_projects):
            state_manager.update_progress(progress, total_projects)

        projects = scrape_all_projects(max_pages=max_pages, progress_callback=progress_callback)
        logger.info(f"Scraping completed. Total projects: {len(projects)}")
        state_manager.finish_scraping(f"Scraping completed. Total projects: {len(projects)}")

        response = ScrapeResponse(projects=projects)
        return response
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        state_manager.finish_scraping(f"Scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@app.get("/scrape/json/range", response_model=ScrapeResponse)
async def scrape_json_range(
    page_from: int = Query(..., ge=1, description="Starting page number (≥ 1)"),
    page_to: int = Query(..., ge=1, description="Ending page number (≥ page_from)")
):
    """
    Scrape project data from jogjasonicindex.com within a page range and return as JSON
    """
    # Check if scraping is already in progress
    if state_manager.is_scraping():
        raise HTTPException(status_code=423, detail="Scraping process is currently in progress. Please wait until it completes or check status at /scrape/status")

    # Validate that page_to is not less than page_from
    if page_to < page_from:
        raise HTTPException(status_code=422, detail="page_to must be greater than or equal to page_from")

    try:
        logger.info(f"Starting JSON scraping process for pages {page_from} to {page_to}...")
        state_manager.start_scraping()

        def progress_callback(progress, total_projects):
            state_manager.update_progress(progress, total_projects)

        projects = scrape_page_range(page_from=page_from, page_to=page_to, progress_callback=progress_callback)
        logger.info(f"Scraping completed. Total projects: {len(projects)}")
        state_manager.finish_scraping(f"Scraping completed. Total projects: {len(projects)}")

        response = ScrapeResponse(projects=projects)
        return response
    except ValueError as e:
        logger.error(f"Validation error during range scraping: {e}")
        state_manager.finish_scraping(f"Scraping failed: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error during range scraping: {e}")
        state_manager.finish_scraping(f"Scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


def flatten_project_data(projects):
    """
    Flatten project data for CSV generation with multiline discography format
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

        # Handle discography - create multiline string for each discography item
        diskografi_list = project.get('diskografi', [])
        diskografi_lines = []

        for disk in diskografi_list:
            tahun = disk.get('tahun', '')
            judul = disk.get('judul', '')
            jenis = disk.get('jenis', '')
            format_val = disk.get('format', '')
            pranala_terkait = ';'.join(disk.get('pranala_terkait', []))

            # Create a line for this discography item
            disk_line = f"{tahun} :: {judul} :: {jenis} :: {format_val} :: {pranala_terkait}"
            diskografi_lines.append(disk_line)

        # Join all discography items with actual newlines
        flat_project['diskografi (tahun :: judul :: jenis :: format :: pranala_terkait)'] = '\n'.join(diskografi_lines)

        flattened_projects.append(flat_project)

    return flattened_projects

def generate_csv_content(projects):
    """
    Generate CSV content from project data with multiline discography format
    """
    if not projects:
        return ""

    # Flatten project data for CSV
    flattened_projects = flatten_project_data(projects)

    # Define the CSV headers based on the expected data fields
    headers = [
        'nama_projek', 'date_posted', 'author', 'deskripsi', 'format',
        'anggota', 'genre', 'tahun', 'status',
        'diskografi (tahun :: judul :: jenis :: format :: pranala_terkait)',
        'pranala', 'tags', 'media'
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
    # Check if scraping is already in progress
    if state_manager.is_scraping():
        raise HTTPException(status_code=423, detail="Scraping process is currently in progress. Please wait until it completes or check status at /scrape/status")

    try:
        logger.info("Starting CSV scraping process...")
        state_manager.start_scraping()

        def progress_callback(progress, total_projects):
            state_manager.update_progress(progress, total_projects)

        projects = scrape_all_projects(max_pages=max_pages, progress_callback=progress_callback)
        logger.info(f"Scraping completed. Total projects: {len(projects)}")
        state_manager.finish_scraping(f"Scraping completed. Total projects: {len(projects)}")

        # Generate CSV content
        csv_content = generate_csv_content(projects)

        # Create a streaming response for the CSV content
        response = StreamingResponse(io.StringIO(csv_content), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=jogjasonicindex_projects.csv"
        return response
    except Exception as e:
        logger.error(f"Error during CSV scraping: {e}")
        state_manager.finish_scraping(f"Scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV scraping failed: {str(e)}")


@app.get("/scrape/csv/range")
async def scrape_csv_range(
    page_from: int = Query(..., ge=1, description="Starting page number (≥ 1)"),
    page_to: int = Query(..., ge=1, description="Ending page number (≥ page_from)")
):
    """
    Scrape project data from jogjasonicindex.com within a page range and return as CSV file
    """
    # Check if scraping is already in progress
    if state_manager.is_scraping():
        raise HTTPException(status_code=423, detail="Scraping process is currently in progress. Please wait until it completes or check status at /scrape/status")

    # Validate that page_to is not less than page_from
    if page_to < page_from:
        raise HTTPException(status_code=422, detail="page_to must be greater than or equal to page_from")

    try:
        logger.info(f"Starting CSV scraping process for pages {page_from} to {page_to}...")
        state_manager.start_scraping()

        def progress_callback(progress, total_projects):
            state_manager.update_progress(progress, total_projects)

        projects = scrape_page_range(page_from=page_from, page_to=page_to, progress_callback=progress_callback)
        logger.info(f"Scraping completed. Total projects: {len(projects)}")
        state_manager.finish_scraping(f"Scraping completed. Total projects: {len(projects)}")

        # Generate CSV content
        csv_content = generate_csv_content(projects)

        # Create a streaming response for the CSV content
        response = StreamingResponse(io.StringIO(csv_content), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=jogjasonicindex_projects.csv"
        return response
    except ValueError as e:
        logger.error(f"Validation error during range scraping: {e}")
        state_manager.finish_scraping(f"Scraping failed: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error during range scraping: {e}")
        state_manager.finish_scraping(f"Scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV scraping failed: {str(e)}")


@app.get("/scrape/status")
async def scrape_status():
    """
    Check the current status of the scraping process
    Returns status and message of the scraping process
    """
    status_info = state_manager.get_status()
    return status_info


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "JSI Scraper API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)
