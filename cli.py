import argparse
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse, urljoin
import os
import pdfkit
from progress_tracker import DownloadProgressTracker
import time
from colorama import init, Fore, Back, Style
from pdf_downloader import PDFDownloader
from url_extractor import extract_urls_from_directory, get_html_file_path
from datetime import datetime
import re

# Initialize colorama
init(autoreset=True)

def setup_logging(log_file='app.log'):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def fetch_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def extract_urls(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    urls = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        if full_url.startswith(('http://', 'https://')):
            urls.add(full_url)
    return urls

def download_or_convert_to_pdf(url, output_dir):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {url}")
        logger.error(str(e))
        return None
    
    content_type = response.headers.get('Content-Type', '').lower()
    
    if 'application/pdf' in content_type:
        filename = os.path.basename(urlparse(url).path) or 'download'
        filename = filename.split('?')[0]  # Remove query parameters from filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_dir, f"{filename}_{timestamp}.pdf")
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"PDF downloaded: {url}")
        return filepath
    else:
        # Fetch the HTML content
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract the title from the HTML
        title = 'Untitled'
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        
        # Remove special characters and replace spaces with underscores
        filename = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        filename = re.sub(r'\s+', '_', filename)
        
        # Add a timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename}_{timestamp}"
        
        filepath = os.path.join(output_dir, f"{filename}.pdf")
        
        # Convert HTML to PDF
        try:
            options = {
                'load-error-handling': 'ignore'
            }
            pdfkit.from_url(url, filepath, options=options)
            logger.info(f"PDF generated: {url}")
            return filepath
        except Exception as e:
            logger.error(f"Error converting {url} to PDF: {str(e)}")
            return None

def process_url(url, output_dir, depth, current_depth=0, processed_urls=None):
    if processed_urls is None:
        processed_urls = set()
    
    if url in processed_urls or current_depth > depth:
        return set()
    
    processed_urls.add(url)
    new_urls = set()
    
    try:
        print(f"{Fore.CYAN}Processing URL: {url}")
        filepath = download_or_convert_to_pdf(url, output_dir)
        if filepath:
            print(f"{Fore.GREEN}Saved: {filepath}")
            
            if current_depth < depth:
                html_content = fetch_content(url)
                extracted_urls = extract_urls(html_content, url)
                for extracted_url in extracted_urls:
                    new_urls.update(process_url(extracted_url, output_dir, depth, current_depth + 1, processed_urls))
        else:
            print(f"{Fore.YELLOW}Failed to process: {url}")
    except Exception as e:
        print(f"{Fore.RED}Error processing {url}: {e}")
    
    return new_urls

def read_urls_from_file(file_path):
    with open(file_path, 'r') as f:
        return {line.strip() for line in f if line.strip()}

def print_welcome_message():
    print(Fore.MAGENTA + Style.BRIGHT + """
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║   Welcome to the Magical PDF Converter!  ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """)
    print(Fore.CYAN + "Prepare to transform the web into beautiful PDFs!")
    print(Fore.YELLOW + "Let's embark on this digital adventure together!\n")

def get_user_choice():
    while True:
        print(Fore.GREEN + "Choose your path, brave explorer:")
        print(Fore.YELLOW + "1. Convert a single URL to PDF")
        print(Fore.BLUE + "2. Crawl a website and convert all links to PDFs")
        print(Fore.MAGENTA + "3. Convert multiple URLs from a file to PDFs")
        choice = input(Fore.WHITE + "Enter your choice (1, 2, or 3): ")
        if choice in ['1', '2', '3']:
            return int(choice)
        else:
            print(Fore.RED + "Oops! That's not a valid choice. Let's try again!")

def get_url_input():
    return input(Fore.CYAN + "Enter the URL you want to convert: ")

def get_website_input():
    url = input(Fore.CYAN + "Enter the website URL you want to crawl: ")
    depth = int(input(Fore.YELLOW + "How deep shall we venture? Enter the crawl depth: "))
    return url, depth

def get_file_input():
    return input(Fore.CYAN + "Enter the path to your file of URLs: ")

def main():
    print_welcome_message()
    
    while True:
        print(Fore.CYAN + "\nMain Menu:")
        print(Fore.YELLOW + "1. Convert URLs to PDFs")
        print(Fore.BLUE + "2. Extract URLs from HTML files")
        print(Fore.GREEN + "3. Process input directory")
        print(Fore.MAGENTA + "4. Exit")
        choice = input(Fore.WHITE + "Enter your choice (1, 2, 3, or 4): ")

        if choice == '1':
            choice = get_user_choice()
            output_dir = "./output"
            os.makedirs(output_dir, exist_ok=True)
            
            progress_tracker = DownloadProgressTracker()
            download_progress = progress_tracker.load_progress() or {}

            if choice == 1:
                url = get_url_input()
                print(Fore.YELLOW + "Preparing to transmute your URL into a PDF...")
                filepath = download_or_convert_to_pdf(url, output_dir)
                if filepath:
                    print(f"{Fore.GREEN}✨ Magic complete! Your PDF awaits at: {filepath}")
                else:
                    print(f"{Fore.RED}Oh no! Our spell fizzled. Unable to convert {url}")

            elif choice == 2:
                url, depth = get_website_input()
                print(Fore.YELLOW + f"Embarking on a magical journey through {url}...")
                urls = process_url(url, output_dir, depth)
                print(Fore.GREEN + f"✨ Adventure complete! Discovered and converted {len(urls)} URLs")

            elif choice == 3:
                file_path = get_file_input()
                urls = read_urls_from_file(file_path)
                print(Fore.YELLOW + f"Preparing to cast our spell on {len(urls)} URLs...")
                downloader = PDFDownloader(concurrency_level=5)
                downloader.download_pdfs(urls, output_dir)
                print(Fore.GREEN + f"✨ Spell casting complete! {downloader.successful_downloads} URLs transformed, {downloader.failed_downloads} URLs resisted magic")

            progress_tracker.save_progress(download_progress)

        elif choice == '2':
            directory = input(Fore.CYAN + "Enter the directory containing HTML files: ")
            filename = input(Fore.YELLOW + "Enter a specific HTML filename (or leave blank for all files): ")
            file_path = get_html_file_path(directory, filename)
            
            if filename:
                urls, base_url = extract_urls_and_base_from_html(file_path)
            else:
                urls, base_url = extract_urls_from_directory(file_path)
            
            print(Fore.GREEN + f"Extracted {len(urls)} unique URLs from {file_path}")
            print(Fore.BLUE + f"Base URL: {base_url}")
        elif choice == '3':
            input_dir = args.input_dir
            output_dir = args.output_dir
            
            # Check if there are pre-existing files in the input directory
            if os.listdir(input_dir):
                print(Fore.YELLOW + f"Input directory '{input_dir}' contains files.")
                process_choice = input(Fore.WHITE + "Do you want to process these files? (Y/N): ")
                
                if process_choice.upper() == 'N':
                    # Clear the input directory
                    for file in os.listdir(input_dir):
                        file_path = os.path.join(input_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    
                    print(Fore.YELLOW + f"Input directory '{input_dir}' cleared.")
                    
                    print(Fore.CYAN + "Please place the HTML files you want to process in the input directory.")
                    input(Fore.WHITE + "Press Enter when you're ready to proceed...")
            
            logger.info(f"Looking for HTML files in: {input_dir}")
            html_files = [f for f in os.listdir(input_dir) if f.endswith('.html')]
            logger.info(f"Files found in the directory: {html_files}")

            urls = set()
            base_url = None
            for html_file in html_files:
                file_path = os.path.join(input_dir, html_file)
                extracted_urls, file_base_url = extract_urls_and_base_from_html(file_path)
                urls.update(extracted_urls)
                if not base_url:
                    base_url = file_base_url

            logger.info(f"Number of unique URLs extracted: {len(urls)}")
            logger.info(f"Base URL detected: {base_url}")

            downloader = PDFDownloader(concurrency_level=args.concurrency)
            logger.info("Starting PDF download process")
            downloader.download_pdfs(urls, output_dir)
            logger.info(f"PDF download process completed. {downloader.successful_downloads} URLs downloaded, {downloader.failed_downloads} URLs failed.")

        elif choice == '4':
            print(Fore.MAGENTA + Style.BRIGHT + "\nThank you for using the Magical Net-Runner!")
            print(Fore.YELLOW + "May your journeys be swift and your discoveries profound!")
            break

        else:
            print(Fore.RED + "Oops! That's not a valid choice. Let's try again!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Net-Runner')
    parser.add_argument('--input-dir', default='./input', help='Input directory for HTML files')
    parser.add_argument('--output-dir', default='./output', help='Output directory for generated PDFs')
    parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'], help='Logging level')
    parser.add_argument('--concurrency', type=int, default=5, help='Number of concurrent downloads')
    args = parser.parse_args()

    print(f"Arguments received: {args}")

    os.makedirs(args.input_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs('./data', exist_ok=True)

    print(f"Directories created/checked: {args.input_dir}, {args.output_dir}, ./data")

    log_dir = '/tmp/logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')
    logging.basicConfig(filename=log_file, level=getattr(logging, args.log_level.upper()), format='%(asctime)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(__name__)
    logger.info("Logging initialized")

    main()