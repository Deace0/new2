import psutil
from log_utils import configure_logging

logger = configure_logging()

class DiskMonitor:
    def __init__(self, config: dict):
        """
        Initialize the DiskMonitor with a configuration.

        Args:
            config (dict): Configuration dictionary for disk settings.
        """
        self.logger = logger
        self.disk_threshold = config.get("disk_threshold", 85)  # Default to 85% if not specified

    def get_usage(self, path: str = "/") -> float | None:
        """
        Returns the current disk usage as a percentage.
        Logs an error if disk usage cannot be retrieved.

        Args:
            path (str): The path to check disk usage for, defaults to the root directory.

        Returns:
            float: Current disk usage percentage.
        """
        try:
            disk_info = psutil.disk_usage(path)
            return disk_info.percent
        except Exception as e:
            self.logger.error(f"Failed to get disk usage: {e}")
            return None

    def check_disk_usage(self, path: str = "/") -> None:
        """
        Checks the current disk usage and logs a warning if it exceeds the threshold.

        Args:
            path (str): The path to check disk usage for, defaults to the root directory.
        """
        usage = self.get_usage(path)
        if usage is not None:
            if usage > self.disk_threshold:
                self.logger.warning(f"High disk usage detected: {usage}% (Threshold: {self.disk_threshold}%)")
            else:
                self.logger.info(f"Current disk usage at {usage}% for path: {path}")
