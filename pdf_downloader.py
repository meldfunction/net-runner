import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
import logging
from urllib.parse import urlparse
import time
import random

class PDFDownloader:
    def __init__(self, concurrency_level=5, log_file='pdf_downloader.log', user_agent=None):
        self.concurrency_level = concurrency_level
        self.logger = self._setup_logger(log_file)
        self.user_agent = user_agent or 'Netrunner PDF Downloader/1.0'
        self.successful_downloads = 0
        self.failed_downloads = 0

    def _setup_logger(self, log_file):
        logger = logging.getLogger('pdf_downloader')
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

    def download_pdf(self, url, output_dir, max_retries=3):
        filename = self._get_filename(url)
        filepath = os.path.join(output_dir, filename)

        headers = {'User-Agent': self.user_agent}

        for attempt in range(max_retries):
            try:
                response = requests.get(url, stream=True, timeout=30, headers=headers)
                response.raise_for_status()

                content_type = response.headers.get('Content-Type', '').lower()
                if 'application/pdf' not in content_type:
                    self.logger.warning(f"Skipping non-PDF content: {url} (Content-Type: {content_type})")
                    self.failed_downloads += 1
                    return False

                file_size = int(response.headers.get('Content-Length', 0))
                if file_size == 0:
                    self.logger.warning(f"Skipping empty file: {url}")
                    self.failed_downloads += 1
                    return False

                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                if os.path.getsize(filepath) > 0:
                    self.logger.info(f"Successfully downloaded: {url}")
                    self.successful_downloads += 1
                    return True
                else:
                    os.remove(filepath)
                    self.logger.warning(f"Downloaded file was empty, deleted: {url}")
                    self.failed_downloads += 1
                    return False

            except requests.RequestException as e:
                self.logger.error(f"Error downloading {url} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(random.uniform(1, 3))  # Random delay between retries

        self.logger.warning(f"Max retries reached for {url}. Skipping.")
        self.failed_downloads += 1
        return False

    def _get_filename(self, url):
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        filename = path.replace('/', '_') or 'index'
        return f"{filename}.pdf"

    def download_pdfs(self, urls, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        with ThreadPoolExecutor(max_workers=self.concurrency_level) as executor:
            future_to_url = {executor.submit(self.download_pdf, url, output_dir): url for url in urls}
            
            with tqdm(total=len(urls), unit="file", desc="Downloading PDFs") as progress_bar:
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        success = future.result()
                        if success:
                            progress_bar.update(1)
                        else:
                            self.logger.warning(f"Failed to download: {url}")
                    except Exception as e:
                        self.logger.error(f"Unexpected error for {url}: {str(e)}")
                        self.failed_downloads += 1

        self.logger.info("PDF download process completed.")