### Prerequisites

- Python 3.x installed on your system
- The following Python libraries installed:
  - `requests`
  - `beautifulsoup4`
  - `tqdm`

You can install the required libraries using pip:

```
pip install requests beautifulsoup4 tqdm
```

### Usage

1. Clone or download the repository containing the "Dredge Runner" script.
2. Navigate to the project directory in your terminal or command prompt.
3. Run the script using the following command:

```
python cli.py -d "path/to/html/files" -o "downloads" -c 10 -l debug
```

This command will:

- Prompt the user to enter the name of the HTML file containing the URLs, located in the `"path/to/html/files"` directory.
- Download the PDFs from the extracted URLs and save them in the `"downloads"` directory.
- Use a concurrency level of 10 to download the PDFs.
- Set the log level to `"debug"` for detailed logging.

The script will display a progress bar showing the overall download progress, and the download details (successful downloads, failed downloads, errors) will be logged to the `"pdf_downloader.log"` file.

### Configuration

The script has the following configurable options:

- `--input-dir` (`-d`): The directory where the HTML file containing the URLs is located.
- `--output-dir` (`-o`): The directory to save the downloaded PDFs.
- `--log-level` (`-l`): The log level (options: `"debug"`, `"info"`, `"warning"`, `"error"`).
- `--concurrency` (`-c`): The number of concurrent downloads to perform.

You can adjust these settings by modifying the corresponding arguments when running the `cli.py` script.

### Resumable Downloads

The "Dredge Runner" script supports resumable downloads, meaning that if a download is interrupted, the script can resume from the last successful checkpoint. The download progress is stored in the `"download_progress.pkl"` file.

### Extensibility and Modularity

The "Dredge Runner" project has been designed with modularity in mind. The script is divided into several components, including URL extraction, PDF downloading, and download progress tracking, allowing for easy maintenance, customization, and future expansion.

If you'd like to contribute to the project or modify the existing functionality, please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for more information.