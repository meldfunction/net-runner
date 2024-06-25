import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_valid_url(url):
    """
    Checks if a given URL is valid.
    Args:
        url (str): The URL to check.
    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and parsed.scheme in ['http', 'https']

def extract_urls_and_base_from_html(file_path):
    """
    Extracts unique URLs and the base URL from the given HTML file.
    Args:
        file_path (str): The path to the HTML file.
    Returns:
        tuple: A set of unique URLs found in the HTML file and the base URL.
    """
    urls = set()
    base_url = None
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        
        # Try to find base URL in the <base> tag
        base_tag = soup.find('base', href=True)
        if base_tag:
            base_url = base_tag['href']
        
        # If no base tag, try to construct from the first absolute URL
        if not base_url:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith(('http://', 'https://')):
                    parsed_url = urlparse(href)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    break
        
        # Extract all URLs
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href) if base_url else href
            if is_valid_url(full_url):
                urls.add(full_url)
    
    return urls, base_url

def extract_urls_from_directory(directory):
    """
    Extracts unique URLs from all HTML files in the given directory.
    Args:
        directory (str): The path to the directory containing HTML files.
    Returns:
        tuple: A set of unique URLs found in all HTML files in the directory and the base URL.
    """
    all_urls = set()
    base_url = None
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            urls, file_base_url = extract_urls_and_base_from_html(file_path)
            all_urls.update(urls)
            if not base_url and file_base_url:
                base_url = file_base_url
    return all_urls, base_url

def get_html_file_path(directory, filename=None):
    """
    Constructs the full path to an HTML file or returns the directory path.
    Args:
        directory (str): The directory containing the HTML file(s).
        filename (str, optional): The name of a specific HTML file.
    Returns:
        str: The full path to the HTML file or directory.
    """
    if filename:
        return os.path.join(directory, filename)
    return directory