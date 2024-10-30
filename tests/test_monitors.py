import os
import pytest
import subprocess
from vm_monitor.service_monitor import ServiceMonitor
from vm_monitor.iptables_monitor import IptablesMonitor
from vm_monitor.user_monitor import UserMonitor
from vm_monitor.cpu_monitor import CPUMonitor
from vm_monitor.memory_monitor import MemoryMonitor
from vm_monitor.disk_monitor import DiskMonitor

LOG_DIR = './test_logs'
WHITELIST_FILE = 'test_service_whitelist.txt'
IPTABLES_SNAPSHOT = 'test_iptables_snapshot.txt'
USER_SNAPSHOT = 'test_user_snapshot.txt'

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    """ Set up logs and clear after each test """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    open(os.path.join(LOG_DIR, WHITELIST_FILE), 'w').close()
    open(os.path.join(LOG_DIR, IPTABLES_SNAPSHOT), 'w').close()
    open(os.path.join(LOG_DIR, USER_SNAPSHOT), 'w').close()
    
    yield

    for file in [WHITELIST_FILE, IPTABLES_SNAPSHOT, USER_SNAPSHOT]:
        file_path = os.path.join(LOG_DIR, file)
        if os.path.exists(file_path):
            os.remove(file_path)

# בדיקות עבור השירותים (Services)
def test_service_monitor_load_whitelist():
    """
    Tests loading the whitelist for services.
    Creates an instance of the ServiceMonitor class with a test whitelist file.
    Asserts that the whitelisted services are loaded as a list and initially empty.
    """
    monitor = ServiceMonitor(log_directory=LOG_DIR, whitelist_file=WHITELIST_FILE)
    assert isinstance(monitor.whitelisted_services, list)
    assert len(monitor.whitelisted_services) == 0

def test_service_monitor_add_service():
    """
    Tests adding a service to the whitelist.
    Creates an instance of the ServiceMonitor class and adds a new service.
    Asserts that the new service is successfully added to the whitelist.
    """
    monitor = ServiceMonitor(log_directory=LOG_DIR, whitelist_file=WHITELIST_FILE)
    monitor.update_whitelist_file("test.service")
    assert "test.service" in monitor.whitelisted_services

# בדיקות עבור iptables
def test_iptables_monitor_initial_snapshot():
    """
    Tests creating an initial iptables snapshot.
    Creates an instance of the IptablesMonitor class.
    Asserts that the iptables snapshot file is created in the specified directory.
    """
    monitor = IptablesMonitor(log_directory=LOG_DIR, iptables_file=IPTABLES_SNAPSHOT)
    assert os.path.exists(os.path.join(LOG_DIR, IPTABLES_SNAPSHOT))

def test_iptables_monitor_compare_rules_with_changes(monkeypatch):
    """
    Tests comparing current iptables rules with the snapshot.
    Mocks the iptables rules and simulates a change in the rules.
    Asserts that the monitor detects the change in the iptables rules.
    """
    def mock_get_current_iptables():
        return '*filter\n:INPUT ACCEPT [0:0]\n-A INPUT -s 192.168.1.1 -j ACCEPT\nCOMMIT\n'
    monkeypatch.setattr(IptablesMonitor, 'get_current_iptables', mock_get_current_iptables)
    monitor = IptablesMonitor(log_directory=LOG_DIR, iptables_file=IPTABLES_SNAPSHOT)
    monitor.save_current_iptables()  # Save initial snapshot
    assert monitor.compare_iptables()  # Changes should be detected

# בדיקות עבור משתמשים (Users)
def test_user_monitor_initial_snapshot():
    """
    Tests creating an initial user snapshot.
    Creates an instance of the UserMonitor class.
    Asserts that the user snapshot file is created in the specified directory.
    """
    monitor = UserMonitor(log_directory=LOG_DIR, users_file=USER_SNAPSHOT)
    assert os.path.exists(os.path.join(LOG_DIR, USER_SNAPSHOT))

# בדיקות עבור שימוש ב-CPU, זיכרון ודיסק
def test_cpu_usage():
    """
    Tests the CPU usage percentage.
    Calls the get_usage method from the CPUMonitor class.
    Asserts that the returned usage is within the valid range of 0 to 100.
    """
    usage = CPUMonitor.get_usage()
    assert usage is not None, "CPU usage returned None"
    assert 0 <= usage <= 100, f"CPU usage out of range: {usage}%"

def test_memory_usage():
    """
    Tests the memory usage percentage.
    Calls the get_usage method from the MemoryMonitor class.
    Asserts that the returned usage is within the valid range of 0 to 100.
    """
    usage = MemoryMonitor.get_usage()
    assert usage is not None, "Memory usage returned None"
    assert 0 <= usage <= 100, f"Memory usage out of range: {usage}%"

def test_disk_usage():
    """
    Tests the disk usage percentage.
    Calls the get_usage method from the DiskMonitor class.
    Asserts that the returned usage is within the valid range of 0 to 100.
    """
    usage = DiskMonitor.get_usage()
    assert usage is not None, "Disk usage returned None"
    assert 0 <= usage <= 100, f"Disk usage out of range: {usage}%"
