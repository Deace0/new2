import psutil
from log_utils import configure_logging

logger = configure_logging()

class CPUMonitor:
    def __init__(self, config: dict):
        """
        Initialize the CPUMonitor with a configuration.

        Args:
            config (dict): Configuration dictionary for CPU settings.
        """
        self.logger = logger
        self.cpu_threshold = config.get("cpu_threshold", 90)  # Default to 90% if not specified

    def get_usage(self, interval: int = 1) -> float | None:
        """
        Returns the current CPU usage as a percentage.
        Logs an error if CPU usage cannot be retrieved.

        Args:
            interval (int): The interval in seconds to calculate CPU usage.

        Returns:
            float: Current CPU usage percentage.
        """
        try:
            return psutil.cpu_percent(interval=interval)
        except Exception as e:
            self.logger.error(f"Failed to get CPU usage: {e}")
            return None

    def check_cpu_usage(self, interval: int = 1) -> None:
        """
        Checks the current CPU usage and logs a warning if it exceeds the threshold.

        Args:
            interval (int): The interval in seconds to calculate CPU usage.
        """
        usage = self.get_usage(interval)
        if usage is not None:
            if usage > self.cpu_threshold:
                self.logger.warning(f"High CPU usage detected: {usage}% (Threshold: {self.cpu_threshold}%)")
            else:
                self.logger.info(f"Current CPU usage is at {usage}%")