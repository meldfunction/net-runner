import os
import requests
import hashlib
import time
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import logging

class PDFDownloader:
    def __init__(self, max_retries=3, retry_delay=2, concurrency_level=5, log_file="pdf_downloader.log"):
        self.MAX_RETRIES = max_retries
        self.RETRY_DELAY = retry_delay
        self.CONCURRENCY_LEVEL = concurrency_level

        # Create the logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create file handler and console handler
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_website_title(self, url):
        """
        Retrieves the title of the website for the given URL.
        Args:
            url (str): The URL of the website.
        Returns:
            str or None: The title of the website, or None if an error occurs.
        """
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title').text.strip()
            return title
        except Exception as e:
            self.logger.error(f"Error getting website title for {url}: {e}")
            return None

    def download_pdf(self, url, output_dir="downloads", resume_data=None):
        """
        Downloads a PDF from the given URL and extracts the filename.
        Args:
            url (str): The URL of the PDF to download.
            output_dir (str, optional): The directory to save the downloaded PDF. Defaults to "downloads".
            resume_data (dict, optional): The download progress data to resume the download.
        Returns:
            str: The filename of the downloaded PDF or None if the download failed.
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Resume the download if resume_data is provided
        start_byte = 0
        if resume_data:
            start_byte = resume_data.get("downloaded_bytes", 0)
            self.logger.info(f"Resuming download from {start_byte} bytes for {url}")

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                # Transform the URL for Google Doc PDF links
                if "docs.google.com" in url:
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    doc_id = query_params.get("id", [None])[0]
                    if doc_id:
                        url = f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"

                headers = {}
                if start_byte > 0:
                    headers["Range"] = f"bytes={start_byte}-"

                response = requests.get(url, stream=True, allow_redirects=True, headers=headers)
                response.raise_for_status()  # Raise exception for non-200 status codes

                # Extract filename from Content-Disposition header (if available)
                filename = response.headers.get('Content-Disposition')
                if filename:
                    # Extract filename from the header (split by ';' and get the second part)
                    filename = filename.split(';')[1].split('=')[1].strip('"')
                else:
                    # Use the website title as the filename if available
                    title = self.get_website_title(url)
                    if title:
                        filename = f"{title.replace(' ', '_')}.pdf"
                    else:
                        filename = f"downloaded_pdf_{url.split('/')[-1]}.pdf"

                # Calculate the SHA-256 hash of the first 1024 bytes (optional)
                pdf_hash = hashlib.sha256(response.content[:1024]).hexdigest()

                # Construct the full output path
                output_path = os.path.join(output_dir, filename)

                # Download the PDF content in chunks
                with open(output_path, 'ab') as f:
                    downloaded_bytes = start_byte
                    for chunk in response.iter_content(1024):
                        if chunk:
                            f.write(chunk)
                            downloaded_bytes += len(chunk)

                self.logger.info(f"Downloaded {filename} (hash: {pdf_hash})")
                print(f"Downloaded {filename} (hash: {pdf_hash})")
                return filename
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error downloading {url} (attempt {attempt}/{self.MAX_RETRIES}): {e}")
                print(f"Error downloading {url} (attempt {attempt}/{self.MAX_RETRIES}): {e}")
                if attempt < self.MAX_RETRIES:
                    self.logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    print(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                    self.RETRY_DELAY *= 2  # Exponential backoff
                else:
                    self.logger.error(f"Maximum retries reached for {url}")
                    print(f"Maximum retries reached for {url}")
                    return None
            except Exception as e:
                self.logger.error(f"Unexpected error while downloading {url}: {e}")
                print(f"Unexpected error while downloading {url}: {e}")
                return None

    def download_pdfs(self, urls, output_dir="downloads"):
        """
        Downloads PDFs from the given list of URLs.
        Args:
            urls (iterable): An iterable of URLs to download PDFs from.
            output_dir (str, optional): The directory to save the downloaded PDFs. Defaults to "downloads".
        """
        successful_downloads = 0
        failed_downloads = 0
        existing_files = set()

        with ThreadPoolExecutor(max_workers=self.CONCURRENCY_LEVEL) as executor, \
             tqdm(total=len(urls), unit="file", desc="Downloading PDFs") as progress_bar:
            futures = [executor.submit(self.download_pdf, url, output_dir) for url in urls]
            for future in futures:
                filename = future.result()
                if filename:
                    if filename in existing_files:
                        self.logger.warning(f"Removed duplicate file: {filename}")
                        print(f"Removed duplicate file: {filename}")
                        os.remove(os.path.join(output_dir, filename))
                    else:
                        existing_files.add(filename)
                        successful_downloads += 1
                else:
                    failed_downloads += 1
                progress_bar.update(1)

        self.logger.info(f"Successful downloads: {successful_downloads}")
        self.logger.info(f"Failed downloads: {failed_downloads}")
        print(f"Successful downloads: {successful_downloads}")
        print(f"Failed downloads: {failed_downloads}")