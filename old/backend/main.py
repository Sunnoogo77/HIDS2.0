from core.monitor_files import FileMonitor
from core.monitor_folders import FolderMonitor
from core.monitor_ips import IPMonitor
import time

# Lancer les moniteurs
file_monitor = FileMonitor()
folder_monitor = FolderMonitor()
ip_monitor = IPMonitor()

file_monitor.start()
folder_monitor.start()
ip_monitor.start()

# Laisser tourner pendant 60s pour voir les changements
try:
    time.sleep(60)
finally:
    file_monitor.stop()
    folder_monitor.stop()
    ip_monitor.stop()
    print("Monitoring stopped.")
