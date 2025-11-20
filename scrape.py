"""
Basic web scraping template
This file serves as a starting point for your web scraping project.
"""
import requests
from bs4 import BeautifulSoup


def scrape_website(url):
    """
    Basic function to scrape a website
    :param url: URL to scrape
    :return: BeautifulSoup object with parsed HTML
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None


# Example usage
if __name__ == "__main__":
    url = "https://example.com"  # Replace with your target website
    soup = scrape_website(url)
    
    if soup:
        print("Page title:", soup.title.string if soup.title else "No title found")
        # Add your scraping logic here