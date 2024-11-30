import threading
import time
import json
from vm_monitor import log_utils, service_monitor
from vm_monitor.cpu_monitor import CPUMonitor
from vm_monitor.memory_monitor import MemoryMonitor
from vm_monitor.disk_monitor import DiskMonitor
from vm_monitor.iptables_monitor import IptablesMonitor
from vm_monitor.user_monitor import UsersMonitor
from vm_monitor.file_monitor import FileIntegrityMonitor


class Monitor:
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the Monitor class.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config = self.load_config(config_file)
        self.check_interval = self.config.get("check_interval", 60)
        self.logger = log_utils.configure_logging()

        self.service_monitor = service_monitor.ServiceMonitor(config=self.config)
        self.iptables_monitor = IptablesMonitor(config=self.config)
        self.users_monitor = UsersMonitor(config=self.config)
        self.memory_monitor = MemoryMonitor(config=self.config)
        self.disk_monitor = DiskMonitor(config=self.config)
        self.cpu_monitor = CPUMonitor(config=self.config)
        self.file_monitor = FileIntegrityMonitor(config=self.config)

    def load_config(self, config_file: str) -> dict:
        """
        Load the configuration from a file.

        Args:
            config_file (str): Path to the configuration file.

        Returns:
            dict: Configuration settings.
        """
        with open(config_file, "r") as f:
            return json.load(f)

    def start_cpu_monitor(self):
        while True:
            self.cpu_monitor.check_cpu_usage()
            time.sleep(self.check_interval)

    def start_memory_monitor(self):
        while True:
            self.memory_monitor.check_memory_usage()
            time.sleep(self.check_interval)
    
    def start_file_monitor(self):
        while True:
            self.file_monitor.monitor_files()
            time.sleep(self.check_interval)

    def start_disk_monitor(self):
        while True:
            self.disk_monitor.check_disk_usage()
            time.sleep(self.check_interval)

    def start_iptables_monitor(self):
        self.iptables_monitor.monitor_iptables()

    def start_users_monitor(self):
        self.users_monitor.monitor_users()

    def start_all_monitors(self):
        """
        Start all monitors in separate threads.
        """
        threading.Thread(target=self.start_cpu_monitor, daemon=True).start()
        threading.Thread(target=self.start_disk_monitor, daemon=True).start()
        threading.Thread(target=self.start_memory_monitor, daemon=True).start()
        threading.Thread(target=self.service_monitor.start_monitoring, daemon=True).start()
        threading.Thread(target=self.start_iptables_monitor, daemon=True).start()
        threading.Thread(target=self.start_users_monitor, daemon=True).start()
        threading.Thread(target=self.start_file_monitor, daemon=True).start()

if __name__ == "__main__":
    monitor = Monitor(config_file="config.json")
    monitor.start_all_monitors()

    while True:
        time.sleep(1)
