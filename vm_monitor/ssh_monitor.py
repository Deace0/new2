import os
import re
import time
from collections import defaultdict
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
        self.max_failures = config["ssh_monitor"]["max_failures"]
        self.fail_pattern = re.compile(r"Failed password for (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+)")
        self.failures = defaultdict(int)

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

                        self.failures[ip] += 1
                        self.logger.info(f"Failed SSH login attempt: User={user}, IP={ip}, Attempts={self.failures[ip]}")

                        if self.failures[ip] >= self.max_failures:
                            self.logger.warning(f"Multiple failed SSH login attempts detected: IP={ip}, Attempts={self.failures[ip]}")
                            self.take_action(ip)
        except Exception as e:
            self.logger.error(f"Error monitoring SSH logins: {str(e)}")

    def take_action(self, ip: str):
        """
        Take action for excessive failed attempts (log or block IP).

        Args:
            ip (str): The offending IP address.
        """
        self.logger.warning(f"Taking action against IP: {ip}")
