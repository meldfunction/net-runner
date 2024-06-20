from bs4 import BeautifulSoup

def extract_urls_from_html(file_path):
    """
    Extracts unique URLs from the given HTML file.
    Args:
        file_path (str): The path to the HTML file.
    Returns:
        set: A set of unique URLs found in the HTML file.
    """
    urls = set()
    with open(file_path, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if href:
                urls.add(href)
    return urls