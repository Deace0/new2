import os
import time
import threading
import subprocess
from log_utils import configure_logging

logger = configure_logging()

class ServiceMonitor:
    def __init__(self, config: dict):
        """
        Initialize the ServiceMonitor class.

        Args:
            config (dict): Configuration dictionary for ServiceMonitor settings.
        """
        self.logger = logger
        self.whitelist_file = os.path.join(config["log_directory"], config["service_monitor"]["whitelist_file"])
        self.check_interval = config["service_monitor"]["check_interval"]
        self.whitelisted_services = self.load_whitelist()

    def load_whitelist(self):
        """
        Loads the whitelist of services from the whitelist file.
        
        Returns:
            list[str]: List of whitelisted services.
        """
        if not os.path.exists(self.whitelist_file):
            self.logger.warning(f"Whitelist file {self.whitelist_file} does not exist. Creating a new one.")
            with open(self.whitelist_file, 'w') as f:
                f.write('')

        with open(self.whitelist_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def get_active_services(self):
        """
        Retrieves the currently active services.

        Returns:
            list[str]: List of active service names.
        """
        try:
            result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running'], stdout=subprocess.PIPE)
            services = result.stdout.decode('utf-8').splitlines()
            active_services = [line.split()[0] for line in services if '.service' in line]
            return active_services
        except Exception as e:
            self.logger.error(f"Error retrieving active services: {str(e)}")
            return []

    def monitor_services(self):
        """
        Monitors services to detect any new ones not in the whitelist.
        Logs if there are no changes detected.
        """
        while True:
            try:
                active_services = self.get_active_services()
                new_services_detected = False
                
                for service in active_services:
                    if service not in self.whitelisted_services:
                        self.logger.warning(f"New service detected: {service}")
                        self.whitelisted_services.append(service)
                        self.update_whitelist_file(service)
                        new_services_detected = True
                
                # Log if no new services were detected
                if not new_services_detected:
                    self.logger.info("No new services detected. All active services are in the whitelist.")
                
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error while monitoring services: {str(e)}")

    def update_whitelist_file(self, service):
        """
        Updates the whitelist file by adding a new service.

        Args:
            service (str): The new service to add to the whitelist.
        """
        try:
            with open(self.whitelist_file, 'a') as f:
                f.write(f"{service}\n")
            self.logger.info(f"Service {service} added to whitelist.")
        except Exception as e:
            self.logger.error(f"Error updating whitelist file: {str(e)}")

    def start_monitoring(self):
        """
        Starts the service monitoring in a separate thread.
        """
        monitor_thread = threading.Thread(target=self.monitor_services)
        monitor_thread.daemon = True
        monitor_thread.start()
