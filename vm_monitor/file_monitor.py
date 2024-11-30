import os
import hashlib
import time
from log_utils import configure_logging

logger = configure_logging()

class FileIntegrityMonitor:
    def __init__(self, config: dict):
        """
        Initialize the File Integrity Monitor.

        Args:
            config (dict): Configuration dictionary for FileIntegrityMonitor settings.
        """
        self.logger = logger
        self.snapshot_file = os.path.join(config["log_directory"], config["file_monitor"]["snapshot_file"])
        self.monitored_files = config["file_monitor"]["monitored_files"]
        self.check_interval = config["file_monitor"]["check_interval"]

        os.makedirs(os.path.dirname(self.snapshot_file), exist_ok=True)

        if not os.path.exists(self.snapshot_file):
            self.logger.info(f"No file integrity snapshot found at {self.snapshot_file}. Saving initial snapshot.")
            self.save_initial_snapshot()

    def hash_file(self, filepath: str) -> str | None:
        """
        Calculate the hash of a file's content.

        Args:
            filepath (str): Path to the file.

        Returns:
            str: The hash of the file's content, or None if the file cannot be read.
        """
        try:
            hasher = hashlib.sha256()
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"Error hashing file {filepath}: {str(e)}")
            return None

    def save_initial_snapshot(self) -> None:
        """
        Save the initial snapshot of monitored files with their hashes.
        """
        try:
            snapshot = {}
            for file in self.monitored_files:
                file_hash = self.hash_file(file)
                if file_hash:
                    snapshot[file] = file_hash
            with open(self.snapshot_file, 'w') as f:
                for filepath, filehash in snapshot.items():
                    f.write(f"{filepath},{filehash}\n")
            self.logger.info(f"Saved initial file integrity snapshot to {self.snapshot_file}.")
        except Exception as e:
            self.logger.error(f"Error saving initial snapshot: {str(e)}")

    def load_snapshot(self) -> dict:
        """
        Load the snapshot of file hashes from the snapshot file.

        Returns:
            dict: A dictionary mapping file paths to their hashes.
        """
        snapshot = {}
        try:
            with open(self.snapshot_file, 'r') as f:
                for line in f:
                    filepath, filehash = line.strip().split(',')
                    snapshot[filepath] = filehash
        except Exception as e:
            self.logger.error(f"Error loading snapshot: {str(e)}")
        return snapshot

    def compare_files(self) -> None:
        """
        Compare current file hashes with the snapshot and log changes.
        """
        current_snapshot = {file: self.hash_file(file) for file in self.monitored_files}
        saved_snapshot = self.load_snapshot()

        for file, current_hash in current_snapshot.items():
            if file not in saved_snapshot:
                self.logger.warning(f"New file detected: {file}")
            elif saved_snapshot[file] != current_hash:
                self.logger.warning(f"File modified: {file}")

        for file in saved_snapshot.keys() - current_snapshot.keys():
            self.logger.warning(f"File removed: {file}")

        self.update_snapshot(current_snapshot)

    def update_snapshot(self, snapshot: dict) -> None:
        """
        Update the snapshot file with the latest file hashes.

        Args:
            snapshot (dict): A dictionary mapping file paths to their hashes.
        """
        try:
            with open(self.snapshot_file, 'w') as f:
                for filepath, filehash in snapshot.items():
                    f.write(f"{filepath},{filehash}\n")
            self.logger.info(f"Updated file integrity snapshot at {self.snapshot_file}.")
        except Exception as e:
            self.logger.error(f"Error updating snapshot: {str(e)}")

    def monitor_files(self) -> None:
        """
        Continuously monitor files for changes.
        """
        while True:
            self.compare_files()
            time.sleep(self.check_interval)
