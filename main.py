from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl
import io
import csv
from typing import Optional, List, Dict, Any
from scrape import scrape_website
from bs4 import BeautifulSoup
import requests

# Pydantic models for request/response validation
class ProjectImage(BaseModel):
    src: str
    alt: str

class ScrapeRequest(BaseModel):
    url: HttpUrl
    max_pages: Optional[int] = None

class ProjectData(BaseModel):
    url: str
    title: str
    project_title: Optional[str] = None
    content: str
    images: List[ProjectImage]
    metadata: Dict[str, Any]

class ScrapeResponse(BaseModel):
    category_url: str
    total_projects: int
    projects: List[ProjectData]

# Create FastAPI instance
app = FastAPI(
    title="JSI Scraper API",
    description="A web scraping API that returns data in JSON or CSV format",
    version="1.0.0"
)

def scrape_category_page(url: str):
    """
    Scrape a category page to get project links
    """
    soup = scrape_website(url)
    if not soup:
        return None
    
    # Extract project links from the category page
    # This is based on general structure - adjust selectors based on actual HTML
    project_links = []
    
    # Look for links that might contain project information
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        # Filter for project-related links (adjust pattern based on site structure)
        if 'projek' in href.lower() or 'project' in href.lower() or '/2025/' in href:
            project_links.append({
                'title': link.get_text(strip=True),
                'url': href
            })
    
    return project_links

def scrape_project_page(url: str):
    """
    Scrape individual project page and extract relevant data
    """
    soup = scrape_website(url)
    if not soup:
        return None
    
    # Extract data from the project page
    # Adjust these selectors to match the actual HTML structure
    project_data = {
        'url': url,
        'title': soup.title.string if soup.title else "",
        'content': "",
        'images': [],
        'metadata': {}
    }
    
    # Extract main content (adjust selectors as needed)
    content_selectors = ['article', '.content', '.post-content', '.entry-content', 'main']
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element:
            project_data['content'] = content_element.get_text(strip=True)
            break
    
    # Extract images
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            project_data['images'].append({
                'src': src,
                'alt': img.get('alt', '')
            })
    
    # Extract metadata (categories, tags, etc.)
    for meta in soup.find_all(['meta', 'span', 'div'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['category', 'tag', 'meta', 'info'])):
        class_name = meta.get('class', [])
        content = meta.get_text(strip=True)
        if content:
            project_data['metadata'][' '.join(class_name)] = content
    
    return project_data

def scrape_all_project_pages(category_url: str):
    """
    Main function to scrape category page and all linked project pages
    """
    # Get project links from category page
    project_links = scrape_category_page(category_url)
    if not project_links:
        return []
    
    all_project_data = []
    
    # Scrape each project page
    for project_link in project_links:
        project_data = scrape_project_page(project_link['url'])
        if project_data:
            project_data['project_title'] = project_link['title']
            all_project_data.append(project_data)
    
    return all_project_data

@app.get("/")
def read_root():
    return {"message": "Welcome to JSI Scraper API", "endpoints": ["/scrape/json", "/scrape/csv"]}

@app.get("/scrape/json", response_model=ScrapeResponse)
async def scrape_json(
    url: str = Query(..., title="Category URL to scrape", description="The URL of the category page to scrape projects from"),
    max_pages: Optional[int] = Query(None, title="Maximum number of pages to scrape", description="Limit the number of project pages to scrape (if None, scrape all)")
):
    """
    Scrape a category page and all linked project pages, return results in JSON format
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    # Validate URL format (basic check)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        all_project_data = scrape_all_project_pages(url)

        if max_pages and max_pages > 0:
            all_project_data = all_project_data[:max_pages]

        # Convert to the expected response format
        result = ScrapeResponse(
            category_url=url,
            total_projects=len(all_project_data),
            projects=[]
        )

        for project in all_project_data:
            # Convert images to ProjectImage format
            project_images = []
            for img in project.get('images', []):
                project_images.append(ProjectImage(
                    src=img.get('src', ''),
                    alt=img.get('alt', '')
                ))

            # Add project data to result
            result.projects.append(ProjectData(
                url=project.get('url', ''),
                title=project.get('title', ''),
                project_title=project.get('project_title'),
                content=project.get('content', ''),
                images=project_images,
                metadata=project.get('metadata', {})
            ))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while scraping: {str(e)}")

@app.get("/scrape/csv")
async def scrape_csv(
    url: str = Query(..., title="Category URL to scrape", description="The URL of the category page to scrape projects from"),
    max_pages: Optional[int] = Query(None, title="Maximum number of pages to scrape", description="Limit the number of project pages to scrape (if None, scrape all)")
):
    """
    Scrape a category page and all linked project pages, return results in CSV format
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    # Validate URL format (basic check)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        all_project_data = scrape_all_project_pages(url)
        
        if max_pages and max_pages > 0:
            all_project_data = all_project_data[:max_pages]
        
        # Prepare CSV data with headers
        csv_data = []
        headers = ["Project Title", "URL", "Page Title", "Content Preview", "Image Count", "Metadata"]
        csv_data.append(headers)
        
        # Add each project as a row
        for project in all_project_data:
            content_preview = project.get('content', '')[:200] + "..." if len(project.get('content', '')) > 200 else project.get('content', '')
            csv_data.append([
                project.get('project_title', ''),
                project.get('url', ''),
                project.get('title', ''),
                content_preview,
                len(project.get('images', [])),
                str(project.get('metadata', {}))
            ])
        
        # Convert to CSV format
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerows(csv_data)
        
        # Create StreamingResponse for CSV download
        stream.seek(0)
        response = StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=jsi_scraped_data.csv"}
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while scraping: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)