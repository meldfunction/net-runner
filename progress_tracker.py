import pickle
import logging

class DownloadProgressTracker:
    def __init__(self, progress_file="download_progress.pkl"):
        self.PROGRESS_FILE = progress_file
        self.logger = logging.getLogger(__name__)

    def save_progress(self, download_progress):
        """
        Saves the download progress to a file.
        Args:
            download_progress (dict): A dictionary containing the download progress data.
        """
        try:
            with open(self.PROGRESS_FILE, 'wb') as f:
                pickle.dump(download_progress, f)
            self.logger.info("Download progress saved.")
        except Exception as e:
            self.logger.error(f"Error saving download progress: {e}")

    def load_progress(self):
        """
        Loads the download progress from a file.
        Returns:
            dict or None: The download progress data, or None if the file doesn't exist or an error occurs.
        """
        try:
            with open(self.PROGRESS_FILE, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f"Error loading download progress: {e}")
            return None