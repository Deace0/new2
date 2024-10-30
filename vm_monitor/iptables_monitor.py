import subprocess
import os
import time
from log_utils import configure_logging

logger = configure_logging()

class IptablesMonitor:
    def __init__(self, config: dict):
        self.logger = logger
        self.snapshot_file = os.path.join(config["log_directory"], config["iptables_monitor"]["snapshot_file"])
        self.check_interval = config["iptables_monitor"]["check_interval"]

        os.makedirs(os.path.dirname(self.snapshot_file), exist_ok=True)

        if not os.path.exists(self.snapshot_file):
            self.logger.info(f"No iptables snapshot found at {self.snapshot_file}. Saving initial snapshot.")
            self.save_initial_iptables_rules()

    def get_current_iptables(self) -> str | None:
        try:
            result = subprocess.run(['iptables-save'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                self.logger.error(f"Error executing iptables-save: {result.stderr.decode('utf-8')}")
                return None
            return result.stdout.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error retrieving iptables rules: {str(e)}")
            return None

    def save_initial_iptables_rules(self) -> None:
        iptables_rules = self.get_current_iptables()
        if iptables_rules:
            try:
                with open(self.snapshot_file, 'w') as f:
                    f.write(iptables_rules)
                self.logger.info(f"Saved initial iptables rules to {self.snapshot_file}.")
            except Exception as e:
                self.logger.error(f"Error saving iptables rules to {self.snapshot_file}: {str(e)}")

    def clean_iptables_rules(self, rules: str) -> str:
        """
        Clean the iptables rules by removing lines that contain dynamic data,
        such as timestamps or packet counters.

        Args:
            rules (str): The iptables rules as a string.

        Returns:
            str: Cleaned iptables rules.
        """
        cleaned_rules = []
        for line in rules.splitlines():
            # Ignore lines that start with "#" (comments) or contain dynamic information like timestamps or counters
            if line.startswith("#") or any(keyword in line for keyword in ["COMMIT", "ACCEPT [", "DROP ["]):
                continue
            cleaned_rules.append(line)
        return "\n".join(cleaned_rules)

    def compare_iptables(self) -> bool:
        current_rules = self.get_current_iptables()
        if not current_rules:
            return False

        current_rules_cleaned = self.clean_iptables_rules(current_rules)

        if os.path.exists(self.snapshot_file):
            with open(self.snapshot_file, 'r') as f:
                saved_rules = f.read()

            saved_rules_cleaned = self.clean_iptables_rules(saved_rules)

            if current_rules_cleaned != saved_rules_cleaned:
                self.logger.warning("Detected changes in iptables rules.")
                return True
            else:
                self.logger.info("No changes detected in iptables rules.")
                return False
        else:
            self.logger.error(f"{self.snapshot_file} does not exist.")
            return False

    def update_iptables_snapshot(self) -> None:
        current_rules = self.get_current_iptables()
        if current_rules:
            try:
                with open(self.snapshot_file, 'w') as f:
                    f.write(current_rules)
                self.logger.info(f"Updated iptables rules in {self.snapshot_file}.")
            except Exception as e:
                self.logger.error(f"Error updating iptables snapshot in {self.snapshot_file}: {str(e)}")

    def monitor_iptables(self) -> None:
        while True:
            if self.compare_iptables():
                self.logger.warning("iptables rules have changed. Updating snapshot.")
                self.update_iptables_snapshot()
            time.sleep(self.check_interval)
