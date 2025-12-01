"""
Web scraping module for jogjasonicindex.com
This file contains functions to scrape project data from jogjasonicindex.com.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for the target website
BASE_URL = "https://jogjasonicindex.com"
CATEGORY_URL = f"{BASE_URL}/category/projek"

# Timeout configuration
REQUEST_TIMEOUT = 30  # seconds for each HTTP request
SCRAPE_TIMEOUT = 1800   # seconds for entire scraping operation (increased to allow scraping up to 160+ projects) - 30 minutes
MAX_RETRIES = 3       # number of retries for failed requests


def get_page_soup(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[BeautifulSoup]:
    """
    Fetch a page and return BeautifulSoup object
    :param url: URL to fetch
    :param timeout: Request timeout in seconds
    :return: BeautifulSoup object with parsed HTML
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout occurred for URL {url}, attempt {attempt + 1}/{MAX_RETRIES}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching the URL {url}: {e}, attempt {attempt + 1}/{MAX_RETRIES}")

        if attempt < MAX_RETRIES - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    return None


def extract_project_links_from_category_page(soup: BeautifulSoup) -> List[str]:
    """
    Extract project links from a category page
    :param soup: BeautifulSoup object of category page
    :return: List of project URLs
    """
    links = []

    # Look for project links in the page
    # Based on HTML analysis, project links are in li.wp-block-post elements with h2.wp-block-post-title > a
    project_items = soup.find_all('li', class_='wp-block-post')

    for item in project_items:
        # Look for links within h2.wp-block-post-title > a
        title_link = item.find('h2', class_='wp-block-post-title')
        if title_link:
            link_tag = title_link.find('a', href=True)
            if link_tag:
                href = link_tag['href']
                if 'jogjasonicindex.com' in href or href.startswith('/'):
                    full_url = urljoin(BASE_URL, href)
                    # Filter for project-specific URLs (avoid other site links)
                    if '/20' in full_url and 'jogjasonicindex.com' in full_url:
                        links.append(full_url)

    # Alternative: Look for any links in post-title or similar classes if the above doesn't work
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
    title_tag = soup.find('h1', class_='wp-block-post-title')
    if title_tag:
        project_data['nama_projek'] = title_tag.get_text().strip()

    # Extract date posted - found in .wp-block-post-date time element
    date_elem = soup.find('div', class_='wp-block-post-date')
    if date_elem:
        time_elem = date_elem.find('time')
        if time_elem:
            project_data['date_posted'] = time_elem.get_text().strip()

    # Extract author - found in .wp-block-post-author element
    author_elem = soup.find('div', class_='wp-block-post-author')
    if author_elem:
        author_name = author_elem.find(class_='wp-block-post-author__name')
        if author_name:
            project_data['author'] = author_name.get_text().strip()

    # Content area for extracting structured data
    content_div = soup.find('div', class_='entry-content') or soup.find('main')

    if content_div:
        # Extract description (text after <strong>Deskripsi</strong>)
        paragraphs = content_div.find_all('p')
        for p in paragraphs:
            strong_tag = p.find('strong')
            if strong_tag and 'deskripsi' in strong_tag.get_text().lower():
                next_p = p.find_next_sibling('p')
                if next_p:
                    project_data['deskripsi'] = next_p.get_text().strip()
                    break

        # Extract format (from buttons after <strong>Format</strong>)
        format_section = None
        for strong in content_div.find_all('strong'):
            if 'format' in strong.get_text().lower():
                format_section = strong.find_parent()
                break

        if format_section:
            buttons_container = format_section.find_next_sibling('div', class_='wp-block-buttons')
            if buttons_container:
                button_links = buttons_container.find_all('a', class_='wp-block-button__link')
                for button_link in button_links:
                    format_val = button_link.get_text().strip()
                    if format_val:
                        project_data['format'] = format_val
                        break

        # Extract anggota (members) - from buttons after <strong>Anggota</strong>
        anggota_section = None
        for strong in content_div.find_all('strong'):
            if 'anggota' in strong.get_text().lower():
                anggota_section = strong.find_parent()
                break

        if anggota_section:
            buttons_container = anggota_section.find_next_sibling('div', class_='wp-block-buttons')
            if buttons_container:
                button_links = buttons_container.find_all('a', class_='wp-block-button__link')
                project_data['anggota'] = []
                for button_link in button_links:
                    member_name = button_link.get_text().strip()
                    if member_name:
                        project_data['anggota'].append(member_name)

        # Extract genre - from buttons after <strong>Genre</strong>
        genre_section = None
        for strong in content_div.find_all('strong'):
            if 'genre' in strong.get_text().lower():
                genre_section = strong.find_parent()
                break

        if genre_section:
            buttons_container = genre_section.find_next_sibling('div', class_='wp-block-buttons')
            if buttons_container:
                button_links = buttons_container.find_all('a', class_='wp-block-button__link')
                for button_link in button_links:
                    genre_val = button_link.get_text().strip()
                    if genre_val:
                        project_data['genre'] = genre_val
                        break

        # Extract tahun (year) - from buttons after <strong>Tahun</strong>
        tahun_section = None
        for strong in content_div.find_all('strong'):
            if 'tahun' in strong.get_text().lower():
                tahun_section = strong.find_parent()
                break

        if tahun_section:
            buttons_container = tahun_section.find_next_sibling('div', class_='wp-block-buttons')
            if buttons_container:
                button_links = buttons_container.find_all('a', class_='wp-block-button__link')
                for button_link in button_links:
                    tahun_val = button_link.get_text().strip()
                    if tahun_val:
                        project_data['tahun'] = tahun_val
                        break

        # Extract status - from buttons after <strong>Status</strong>
        status_section = None
        for strong in content_div.find_all('strong'):
            if 'status' in strong.get_text().lower():
                status_section = strong.find_parent()
                break

        if status_section:
            buttons_container = status_section.find_next_sibling('div', class_='wp-block-buttons')
            if buttons_container:
                button_links = buttons_container.find_all('a', class_='wp-block-button__link')
                for button_link in button_links:
                    status_val = button_link.get_text().strip()
                    if status_val:
                        project_data['status'] = status_val
                        break

        # Extract discography from table after <strong>Diskografi</strong>
        diskografi_section = None
        for strong in content_div.find_all('strong'):
            if 'diskografi' in strong.get_text().lower():
                diskografi_section = strong.find_parent()
                break

        if diskografi_section:
            table = diskografi_section.find_next('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:  # Need at least tahun, judul, jenis, format
                        disc_item = {
                            'tahun': cells[0].get_text().strip(),
                            'judul': cells[1].get_text().strip(),
                            'jenis': cells[2].get_text().strip(),
                            'format': cells[3].get_text().strip(),
                            'pranala_terkait': []
                        }
                        # Extract links from the row
                        links_in_row = row.find_all('a', href=True)
                        for link in links_in_row:
                            disc_item['pranala_terkait'].append(link['href'])
                        project_data['diskografi'].append(disc_item)

        # Extract pranala (links) - from buttons after <strong>Pranala</strong>
        pranala_section = None
        for strong in content_div.find_all('strong', string='Pranala'):
            if 'pranala' in strong.get_text().lower():
                pranala_section = strong.find_parent()
                break

        if pranala_section:
            buttons_container = pranala_section.find_next_sibling('div', class_='wp-block-buttons')
            if buttons_container:
                button_links = buttons_container.find_all('a', class_='wp-block-button__link', href=True)
                project_data['pranala'] = []
                for button_link in button_links:
                    href = button_link['href']
                    project_data['pranala'].append(href)

    # Extract media (images from gallery)
    gallery = soup.find('figure', class_='wp-block-gallery')
    if gallery:
        img_tags = gallery.find_all('img')
        for img in img_tags:
            src = img.get('src')
            if src and 'jogjasonicindex.com' in src:
                # Clean up the src URL by removing query parameters
                clean_src = src.split('?')[0]
                project_data['media'].append(clean_src)

    # Extract tags from taxonomy-post_tag elements after "Tags" text
    for p_tag in soup.find_all('p', string=lambda text: text and 'Tags' in text):
        tags_container = p_tag.find_next_sibling('div', class_='taxonomy-post_tag')
        if tags_container:
            tag_links = tags_container.find_all('a', href=True)
            for tag_link in tag_links:
                tag_text = tag_link.get_text().strip()
                if tag_text:
                    project_data['tags'].append(tag_text)
            break

    # Remove duplicates from lists
    project_data['pranala'] = list(set(project_data['pranala']))
    project_data['tags'] = list(set(project_data['tags']))
    project_data['media'] = list(set(project_data['media']))

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

    # Look for pagination in nav.wp-block-query-pagination (WordPress Gutenberg block)
    pagination_nav = soup.find('nav', class_='wp-block-query-pagination')
    if pagination_nav:
        page_links = pagination_nav.find_all('a', class_='page-numbers')
        for link in page_links:
            href = link.get('href', '')
            if 'page/' in href:
                try:
                    page_num = int(href.split('page/')[1].split('/')[0])
                    if page_num > max_page:
                        max_page = page_num
                except (ValueError, IndexError):
                    continue

        # Also check for the last page number directly in .page-numbers
        last_page_link = pagination_nav.find_all('a', class_='page-numbers')[-1:]  # Get the last element
        if last_page_link:
            href = last_page_link[0].get('href', '')
            if 'page/' in href:
                try:
                    page_num = int(href.split('page/')[1].split('/')[0])
                    if page_num > max_page:
                        max_page = page_num
                except (ValueError, IndexError):
                    pass

    # Alternative: look for page links in the page if Gutenberg pagination not found
    if max_page == 1:  # If no pagination found via Gutenberg blocks
        page_links = soup.find_all('a', href=True)
        for link in page_links:
            href = link['href']
            if 'page/' in href and 'jogjasonicindex.com/category/projek' in href:
                try:
                    page_num = int(href.split('page/')[1].split('/')[0])
                    if page_num > max_page:
                        max_page = page_num
                except (ValueError, IndexError):
                    continue

    # If no pagination links found, return 1 (only one page)
    if max_page == 1:
        # Check if there's a "Next" button but no numbered links
        next_button = soup.find('a', class_='wp-block-query-pagination-next')
        if next_button:
            max_page = 2  # At least 2 pages if there's a next button

    return max_page


def scrape_all_projects(max_pages: Optional[int] = None, progress_callback=None) -> List[Dict]:
    """
    Scrape all projects from all category pages
    :param max_pages: Maximum number of pages to scrape (None for all pages)
    :param progress_callback: Optional callback function to report progress updates
    :return: List of project data dictionaries
    """
    all_projects = []
    page_num = 1
    total_pages = get_total_category_pages()

    if max_pages and max_pages < total_pages:
        total_pages = max_pages

    logger.info(f"Starting to scrape {total_pages} category pages...")

    # If progress callback is provided, update initial progress
    if progress_callback:
        progress_callback(0, 0)  # Initial progress: 0%

    # Add timeout to the entire scraping operation
    start_time = time.time()

    # Count total projects for progress calculation
    total_projects_expected = 0
    if max_pages is None:
        # Calculate total expected projects by scanning all pages first
        temp_page = 1
        while temp_page <= total_pages:
            if temp_page == 1:
                category_url = CATEGORY_URL
            else:
                category_url = f"{CATEGORY_URL}/page/{temp_page}"

            category_soup = get_page_soup(category_url)
            if category_soup:
                project_links = extract_project_links_from_category_page(category_soup)
                total_projects_expected += len(project_links)
            temp_page += 1

    current_project_index = 0
    total_projects_to_process = total_projects_expected

    while page_num <= total_pages:
        # Check if we're approaching timeout
        elapsed_time = time.time() - start_time
        if elapsed_time > SCRAPE_TIMEOUT * 0.8:  # Use 80% of timeout to be safe
            logger.warning(f"Approaching timeout, stopping early. Scraped {len(all_projects)} projects so far.")
            if progress_callback:
                progress = min(100, int((len(all_projects) / total_projects_to_process) * 100)) if total_projects_to_process > 0 else 0
                progress_callback(progress, len(all_projects))
            break

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
            # Check timeout before scraping each project
            elapsed_time = time.time() - start_time
            if elapsed_time > SCRAPE_TIMEOUT * 0.8:
                logger.warning(f"Approaching timeout, stopping early. Scraped {len(all_projects)} projects so far.")
                if progress_callback:
                    progress = min(100, int((len(all_projects) / total_projects_to_process) * 100)) if total_projects_to_process > 0 else 0
                    progress_callback(progress, len(all_projects))
                return all_projects

            logger.info(f"Scraping project {i+1}/{len(project_links)} on page {page_num}: {project_url}")

            project_soup = get_page_soup(project_url)
            if project_soup:
                project_data = extract_project_data_from_page(project_soup, project_url)
                project_data['source_url'] = project_url  # Add source URL for reference
                all_projects.append(project_data)

                # Update progress
                current_project_index += 1
                if progress_callback and total_projects_to_process > 0:
                    progress = min(100, int((current_project_index / total_projects_to_process) * 100))
                    progress_callback(progress, len(all_projects))

                # Add a smaller delay to be respectful to the server but more efficient
                time.sleep(0.2)
            else:
                logger.warning(f"Failed to scrape project: {project_url}")

                # Still update progress even if scraping failed
                current_project_index += 1
                if progress_callback and total_projects_to_process > 0:
                    progress = min(100, int((current_project_index / total_projects_to_process) * 100))
                    progress_callback(progress, len(all_projects))

        page_num += 1

    logger.info(f"Scraping completed! Total projects scraped: {len(all_projects)}")
    if progress_callback:
        progress_callback(100, len(all_projects))  # Final progress: 100%

    return all_projects


def scrape_single_category_page(page_num: int = 1, progress_callback=None) -> List[Dict]:
    """
    Scrape a single category page (for testing or partial scraping)
    :param page_num: Page number to scrape (1 for first page)
    :param progress_callback: Optional callback function to report progress updates
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
    projects = scrape_all_projects(max_pages=2, progress_callback=None)  # Limit to 2 pages for testing
    print(f"Scraped {len(projects)} projects")
    for i, project in enumerate(projects[:3]):  # Print first 3 projects as sample
        print(f"\nProject {i+1}:")
        for key, value in project.items():
            print(f"  {key}: {value}")
