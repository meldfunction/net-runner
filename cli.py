import argparse
from url_extractor import extract_urls_from_html, get_html_file_path
from pdf_downloader import PDFDownloader
from progress_tracker import DownloadProgressTracker
import logging
import os

def get_command_line_arguments():
    """
    Parses the command-line arguments for the PDF downloader script.
    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="PDF downloader script")
    parser.add_argument("-d", "--input-dir", default=".", help="Directory containing the HTML file")
    parser.add_argument("-o", "--output-dir", default="/app/downloads", help="Directory to save the downloaded PDFs")
    parser.add_argument("-l", "--log-level", default="info", choices=["debug", "info", "warning", "error"], help="Set the log level")
    parser.add_argument("-c", "--concurrency", type=int, default=5, help="Number of concurrent downloads")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_command_line_arguments()

    # Set the log level based on the user's input
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # Get the HTML file path from the user
    html_file_path = get_html_file_path(args.input_dir)

    # Extract URLs from the HTML file
    urls = extract_urls_from_html(html_file_path)
    print(f"Number of unique URLs: {len(urls)}")

    # Initialize the PDF downloader and download progress tracker
    pdf_downloader = PDFDownloader(concurrency_level=args.concurrency, log_file="/app/pdf_downloader.log")
    progress_tracker = DownloadProgressTracker(progress_file="/app/download_progress.pkl")

    # Load the download progress
    download_progress = progress_tracker.load_progress()

    # Run the PDF downloader
    pdf_downloader.download_pdfs(urls, args.output_dir)
    logger.info("PDF download script completed.")

    # Save the final download progress
    progress_tracker.save_progress(download_progress)

    # Run the tests
    unittest.main()