```markdown
# Dredge Runner Usage Guide

Dredge Runner can be run either directly with Python or using Docker. Choose the method that best suits your environment and preferences.

## Method 1: Running with Python

### Prerequisites
- Python 3.x
- Required Python libraries: `requests`, `beautifulsoup4`, `tqdm`

Install the required libraries:
```
pip install requests beautifulsoup4 tqdm
```

### Usage
1. Clone or download the Dredge Runner repository.
2. Navigate to the project directory in your terminal.
3. Run the script:

```
python cli.py -d "path/to/html/files" -o "downloads" -c 10 -l debug
```

## Method 2: Running with Docker

### Prerequisites
- Docker installed on your system

### Building the Docker Image
1. Navigate to the project directory containing the Dockerfile.
2. Build the Docker image:

```
docker build -t dredge-runner .
```

### Running the Docker Container

```
docker run -v /path/to/local/input:/app/input -v /path/to/local/output:/app/output dredge-runner -d "/app/input" -o "/app/output" -c 10 -l debug
```

Replace `/path/to/local/input` with your local input directory path and `/path/to/local/output` with your desired output directory path.

## Configuration Options

Both methods use the same configuration options:

- `--input-dir` (`-d`): Directory containing the HTML file with URLs.
- `--output-dir` (`-o`): Directory to save downloaded PDFs.
- `--log-level` (`-l`): Log level (`debug`, `info`, `warning`, `error`).
- `--concurrency` (`-c`): Number of concurrent downloads.

## Workflow

Regardless of the method chosen, Dredge Runner will:

1. Prompt for the HTML file name in the input directory.
2. Extract URLs from the HTML file.
3. Download PDFs from the extracted URLs to the output directory.
4. Display a progress bar for overall download progress.
5. Log download details to `pdf_downloader.log`.

## Resumable Downloads

Dredge Runner supports resuming interrupted downloads. Progress is saved in `download_progress.pkl`.

## Extensibility

The project is modular, allowing for easy maintenance and customization. For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).
```

This updated USAGE.md now clearly presents both methods of running Dredge Runner (Python and Docker), provides the necessary commands for each, and maintains a consistent structure for easy comprehension. It also retains important information about configuration options, workflow, resumable downloads, and extensibility.