import os
import re
import time
from log_utils import configure_logging

logger = configure_logging()

class SSHMonitor:
    def __init__(self, config: dict):
        """
        Initialize the SSH Monitor.

        Args:
            config (dict): Configuration dictionary for SSHMonitor settings.
        """
        self.logger = logger
        self.log_file = config["ssh_monitor"]["log_file"]
        self.check_interval = config["ssh_monitor"]["check_interval"]
        self.fail_pattern = re.compile(r"Failed password for (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+)")

        if not os.path.exists(self.log_file):
            self.logger.error(f"Log file {self.log_file} does not exist. Please ensure the path is correct.")
            raise FileNotFoundError(f"{self.log_file} not found.")

    def monitor_ssh_failures(self):
        """
        Continuously monitor the log file for failed SSH login attempts.
        """
        try:
            with open(self.log_file, 'r') as log:
                log.seek(0, os.SEEK_END) 
                while True:
                    line = log.readline()
                    if not line:
                        time.sleep(self.check_interval)
                        continue

                    match = self.fail_pattern.search(line)
                    if match:
                        user = match.group("user")
                        ip = match.group("ip")
                        self.logger.warning(f"Failed SSH login detected: User={user}, IP={ip}")
        except Exception as e:
            self.logger.error(f"Error monitoring SSH logins: {str(e)}")
