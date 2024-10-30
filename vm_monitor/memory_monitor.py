import psutil
from log_utils import configure_logging

logger = configure_logging()

class MemoryMonitor:
    def __init__(self, config: dict):
        """
        Initialize the MemoryMonitor with a configuration.

        Args:
            config (dict): Configuration dictionary for memory settings.
        """
        self.logger = logger
        self.memory_threshold = config.get("memory_threshold", 80)  # Default to 80% if not specified

    def get_usage(self) -> float | None:
        """
        Returns the current memory usage as a percentage.
        Logs an error if memory usage cannot be retrieved.

        Returns:
            float: Current memory usage percentage.
        """
        try:
            memory_info = psutil.virtual_memory()
            return memory_info.percent
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return None

    def check_memory_usage(self) -> None:
        """
        Checks the current memory usage and logs a warning if it exceeds the threshold.
        """
        usage = self.get_usage()
        if usage is not None:
            if usage > self.memory_threshold:
                self.logger.warning(f"High memory usage detected: {usage}% (Threshold: {self.memory_threshold}%)")
            else:
                self.logger.info(f"Current memory usage is at {usage}%")
