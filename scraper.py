"""
Web scraping module for jogjasonicindex.com
This file contains functions to scrape project data from jogjasonicindex.com.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import logging
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for the target website
BASE_URL = "https://jogjasonicindex.com"
CATEGORY_URL = f"{BASE_URL}/category/projek"


def get_page_soup(url: str) -> Optional[BeautifulSoup]:
    """
    Fetch a page and return BeautifulSoup object
    :param url: URL to fetch
    :return: BeautifulSoup object with parsed HTML
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching the URL {url}: {e}")
        return None


def extract_project_links_from_category_page(soup: BeautifulSoup) -> List[str]:
    """
    Extract project links from a category page
    :param soup: BeautifulSoup object of category page
    :return: List of project URLs
    """
    links = []
    
    # Look for project links in the page
    # WordPress usually has articles/posts in <article> tags or <div> with specific classes
    articles = soup.find_all('article')
    
    for article in articles:
        # Look for links within the article
        link_tags = article.find_all('a', href=True)
        for link_tag in link_tags:
            href = link_tag['href']
            if 'jogjasonicindex.com' in href or href.startswith('/'):
                full_url = urljoin(BASE_URL, href)
                # Filter for project-specific URLs (avoid other site links)
                if '/20' in full_url and 'jogjasonicindex.com' in full_url:
                    links.append(full_url)
    
    # Alternative: Look for links in post-title or similar classes
    if not links:
        title_links = soup.find_all('a', class_=lambda x: x and 'title' in x.lower())
        for link in title_links:
            href = link.get('href')
            if href:
                full_url = urljoin(BASE_URL, href)
                if '/20' in full_url and 'jogjasonicindex.com' in full_url:
                    links.append(full_url)

    # Remove duplicates while preserving order
    unique_links = []
    for link in links:
        if link not in unique_links:
            unique_links.append(link)
    
    return unique_links


def extract_project_data_from_page(soup: BeautifulSoup, project_url: str) -> Dict:
    """
    Extract project data from a project page
    :param soup: BeautifulSoup object of project page
    :param project_url: URL of the project page
    :return: Dictionary with project data
    """
    project_data = {
        'nama_projek': None,
        'date_posted': None,
        'author': None,
        'deskripsi': None,
        'format': None,
        'anggota': [],
        'genre': None,
        'tahun': None,
        'status': None,
        'diskografi': [],
        'pranala': [],
        'tags': [],
        'media': []
    }
    
    # Extract project name from title
    title_tag = soup.find('h1', class_=lambda x: x and 'title' in x.lower())
    if not title_tag:
        title_tag = soup.find('title')
    if title_tag:
        project_data['nama_projek'] = title_tag.get_text().strip()
    
    # Extract content area (description and other details)
    content_div = soup.find('div', class_=lambda x: x and 'content' in x.lower())
    if not content_div:
        content_div = soup.find('main') or soup.find('article')
    
    if content_div:
        # Extract description (usually the main content)
        paragraphs = content_div.find_all('p')
        if paragraphs:
            descriptions = []
            for p in paragraphs:
                text = p.get_text().strip()
                # Skip empty paragraphs
                if text and 'projek' in text.lower():
                    descriptions.append(text)
            if descriptions:
                project_data['deskripsi'] = ' '.join(descriptions)[:500]  # Limit description length

        # Look for specific fields like format, genre, etc.
        # These are often in sidebars, meta info, or structured content
        all_text = content_div.get_text()
        
        # Extract year if mentioned in the text
        import re
        year_matches = re.findall(r'\b(19|20)\d{2}\b', all_text)
        if year_matches:
            project_data['tahun'] = year_matches[0]
        
        # Look for format (group/solo)
        format_keywords = ['group', 'solo', 'duo', 'trio']
        for keyword in format_keywords:
            if keyword in all_text.lower():
                project_data['format'] = keyword
                break
        
        # Look for status (aktif/bubar)
        status_keywords = ['aktif', 'bubar', 'aktif', 'masih aktif', 'dibubarkan']
        for keyword in status_keywords:
            if keyword in all_text.lower():
                project_data['status'] = 'aktif' if any(active in keyword for active in ['aktif', 'masih']) else 'bubar'
                break

    # Extract author information
    author_elem = soup.find('span', class_=lambda x: x and 'author' in x.lower())
    if not author_elem:
        author_elem = soup.find('a', class_=lambda x: x and 'author' in x.lower())
    if author_elem:
        project_data['author'] = author_elem.get_text().strip()
    
    # Extract date posted
    date_elem = soup.find('time')
    if not date_elem:
        date_elem = soup.find('span', class_=lambda x: x and any(d in x.lower() for d in ['date', 'time']))
    if date_elem:
        project_data['date_posted'] = date_elem.get_text().strip()

    # Extract media (images)
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src')
        if src and 'jogjasonicindex.com' in src:
            project_data['media'].append(src)
    
    # Remove duplicates from media list
    project_data['media'] = list(set(project_data['media']))

    # Extract links (pranala)
    link_tags = soup.find_all('a', href=True)
    for link in link_tags:
        href = link['href']
        if any(domain in href for domain in ['youtube.com', 'bandcamp.com', 'soundcloud.com', 'spotify.com']):
            project_data['pranala'].append(href)
    
    # Remove duplicates from pranala list
    project_data['pranala'] = list(set(project_data['pranala']))

    # Extract tags
    tag_elements = soup.find_all(['span', 'a'], class_=lambda x: x and 'tag' in x.lower())
    for tag_elem in tag_elements:
        tag_text = tag_elem.get_text().strip()
        if tag_text:
            project_data['tags'].append(tag_text)
    
    # Extract genre if available
    # Look for genre in text content
    if content_div:
        text_content = content_div.get_text().lower()
        genre_keywords = ['genre', 'aliran', 'style', 'jenis', 'type']
        for keyword in genre_keywords:
            if keyword in text_content:
                # Look for text after the keyword
                parts = text_content.split(keyword)
                if len(parts) > 1:
                    # Get the part after the keyword and extract first meaningful word
                    after_keyword = parts[1].strip()
                    words = after_keyword.split()[:5]  # Look at first 5 words
                    for word in words:
                        if len(word) > 2 and not word.startswith('(') and not word.endswith(')'):
                            project_data['genre'] = word
                            break
                    if project_data['genre']:
                        break
    
    # Extract discography (if table exists)
    # Look for tables that might contain discography info
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 1:  # If table has multiple rows, likely discography
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:  # At least year and title
                    disc_item = {
                        'tahun': cells[0].get_text().strip() if len(cells) > 0 else None,
                        'judul': cells[1].get_text().strip() if len(cells) > 1 else None,
                        'jenis': cells[2].get_text().strip() if len(cells) > 2 else None,
                        'format': cells[3].get_text().strip() if len(cells) > 3 else None,
                        'pranala': []
                    }
                    
                    # Extract any links from the row
                    links_in_row = row.find_all('a', href=True)
                    for link in links_in_row:
                        disc_item['pranala'].append(link['href'])
                    
                    project_data['diskografi'].append(disc_item)

    # Extract members (anggota)
    # Look for member information in the content
    if content_div:
        content_text = content_div.get_text()
        # Look for keywords related to members
        member_keywords = ['anggota', 'member', 'personil', 'personnel']
        for keyword in member_keywords:
            if keyword in content_text.lower():
                # This is a simplified approach - in reality, member extraction would need to be
                # more specific to the website's structure
                # For now, we'll just mark that members should be extracted
                pass

    return project_data


def get_total_category_pages() -> int:
    """
    Get the total number of category pages by examining pagination
    :return: Total number of pages
    """
    soup = get_page_soup(CATEGORY_URL)
    if not soup:
        return 1
    
    # Look for pagination links
    max_page = 1
    
    # Look for page links in the page
    page_links = soup.find_all('a', href=True)
    for link in page_links:
        href = link['href']
        if 'page/' in href:
            try:
                page_num = int(href.split('page/')[1].split('/')[0])
                if page_num > max_page:
                    max_page = page_num
            except (ValueError, IndexError):
                continue
    
    # Alternative: look for page numbers in navigation elements
    nav_elements = soup.find_all(['div', 'nav', 'ul'], class_=lambda x: x and any(p in x.lower() for p in ['page', 'nav', 'pagination']))
    for nav in nav_elements:
        links = nav.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'page/' in href:
                try:
                    page_num = int(href.split('page/')[1].split('/')[0])
                    if page_num > max_page:
                        max_page = page_num
                except (ValueError, IndexError):
                    continue
    
    return max_page


def scrape_all_projects(max_pages: Optional[int] = None) -> List[Dict]:
    """
    Scrape all projects from all category pages
    :param max_pages: Maximum number of pages to scrape (None for all pages)
    :return: List of project data dictionaries
    """
    all_projects = []
    page_num = 1
    total_pages = get_total_category_pages()
    
    if max_pages and max_pages < total_pages:
        total_pages = max_pages
    
    logger.info(f"Starting to scrape {total_pages} category pages...")
    
    while page_num <= total_pages:
        # Construct category page URL
        if page_num == 1:
            category_url = CATEGORY_URL
        else:
            category_url = f"{CATEGORY_URL}/page/{page_num}"
        
        logger.info(f"Scraping category page {page_num}: {category_url}")
        
        # Get category page soup
        category_soup = get_page_soup(category_url)
        if not category_soup:
            logger.warning(f"Failed to get category page {page_num}, skipping...")
            page_num += 1
            continue
        
        # Extract project links from this category page
        project_links = extract_project_links_from_category_page(category_soup)
        logger.info(f"Found {len(project_links)} project links on page {page_num}")
        
        # Scrape each project page
        for i, project_url in enumerate(project_links):
            logger.info(f"Scraping project {i+1}/{len(project_links)} on page {page_num}: {project_url}")
            
            project_soup = get_page_soup(project_url)
            if project_soup:
                project_data = extract_project_data_from_page(project_soup, project_url)
                project_data['source_url'] = project_url  # Add source URL for reference
                all_projects.append(project_data)
                
                # Add a small delay to be respectful to the server
                time.sleep(0.5)
            else:
                logger.warning(f"Failed to scrape project: {project_url}")
        
        page_num += 1
    
    logger.info(f"Scraping completed! Total projects scraped: {len(all_projects)}")
    return all_projects


def scrape_single_category_page(page_num: int = 1) -> List[Dict]:
    """
    Scrape a single category page (for testing or partial scraping)
    :param page_num: Page number to scrape (1 for first page)
    :return: List of project data dictionaries
    """
    all_projects = []
    
    # Construct category page URL
    if page_num == 1:
        category_url = CATEGORY_URL
    else:
        category_url = f"{CATEGORY_URL}/page/{page_num}"
    
    logger.info(f"Scraping category page {page_num}: {category_url}")
    
    # Get category page soup
    category_soup = get_page_soup(category_url)
    if not category_soup:
        logger.error(f"Failed to get category page {page_num}")
        return all_projects
    
    # Extract project links from this category page
    project_links = extract_project_links_from_category_page(category_soup)
    logger.info(f"Found {len(project_links)} project links on page {page_num}")
    
    # Scrape each project page
    for i, project_url in enumerate(project_links):
        logger.info(f"Scraping project {i+1}/{len(project_links)}: {project_url}")
        
        project_soup = get_page_soup(project_url)
        if project_soup:
            project_data = extract_project_data_from_page(project_soup, project_url)
            project_data['source_url'] = project_url  # Add source URL for reference
            all_projects.append(project_data)
            
            # Add a small delay to be respectful to the server
            time.sleep(0.5)
        else:
            logger.warning(f"Failed to scrape project: {project_url}")
    
    return all_projects


if __name__ == "__main__":
    # Example usage
    projects = scrape_all_projects(max_pages=2)  # Limit to 2 pages for testing
    print(f"Scraped {len(projects)} projects")
    for i, project in enumerate(projects[:3]):  # Print first 3 projects as sample
        print(f"\nProject {i+1}:")
        for key, value in project.items():
            print(f"  {key}: {value}")