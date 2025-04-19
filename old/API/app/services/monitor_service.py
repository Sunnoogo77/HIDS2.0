# import asyncio
# import subprocess
# import os

# class MonitorService:
#     def __init__(self):
#         self.scripts_dir = "../Core/scripts"

#     async def run_powershell_script(self, script_name, args=None):
#         """
#         Run a PowerShell script asynchronously.
#         """
#         script_path = os.path.join(self.scripts_dir, script_name)
#         command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]
#         if args:
#             command.extend(args)

#         process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         stdout, stderr = await process.communicate()
#         return stdout.decode(), stderr.decode()

#     async def start_monitoring(self, monitor_types):
#         """
#         Launches the specified monitoring types asynchronously.
#         """
#         tasks = []
#         if "files" in monitor_types:
#             tasks.append(self.run_powershell_script("monitor_files.ps1"))
#         if "folders" in monitor_types:
#             tasks.append(self.run_powershell_script("monitor_folders.ps1"))
#         if "ips" in monitor_types:
#             tasks.append(self.run_powershell_script("monitor_ips.ps1"))
#         if "emails" in monitor_types:
#             tasks.append(self.run_powershell_script("alerts.ps1"))
#         results = await asyncio.gather(*tasks)
#         return results

#     async def stop_monitoring(self, monitor_type):
#         """
#         Stop monitoring (files, folders, IPs, mails).
#         """
#         if monitor_type == "files":
#             output = await self.run_powershell_script("stop_monitor_files.ps1")
#         elif monitor_type == "folders":
#             output = await self.run_powershell_script("stop_monitor_folders.ps1")
#         elif monitor_type == "ips":
#             output = await self.run_powershell_script("stop_monitor_ips.ps1")
#         elif monitor_type == "emails":
#             output = await self.run_powershell_script("stop_monitor_emails.ps1")
#         else:
#             raise ValueError("Invalid monitor type")
#         return output

#-------------------------------------------------------

# import asyncio
# import subprocess
# import os
# import logging

# class MonitorService:
#     def __init__(self):
#         self.scripts_dir = os.path.abspath("../Core/scripts")
#         logging.basicConfig(level=logging.INFO)

#     async def run_powershell_script(self, script_name, args=None):
#         """Run a PowerShell script asynchronously."""
#         script_path = os.path.join(self.scripts_dir, script_name)
#         command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]
#         if args:
#             command.extend(args)

#         logging.info(f"Running PowerShell script: {script_path}")
#         process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         stdout, stderr = await process.communicate()
#         stdout_decoded, stderr_decoded = stdout.decode(), stderr.decode()
#         logging.info(f"PowerShell script output: {stdout_decoded}, error: {stderr_decoded}")
#         return stdout_decoded, stderr_decoded

#     async def start_monitoring(self, monitor_types):
#         """Launches the specified monitoring types asynchronously."""
#         tasks = []
#         if "files" in monitor_types:
#             tasks.append(self.run_powershell_script("monitor_files.ps1"))
#         if "folders" in monitor_types:
#             tasks.append(self.run_powershell_script("monitor_folders.ps1"))
#         if "ips" in monitor_types:
#             tasks.append(self.run_powershell_script("monitor_ips.ps1"))
#         if "emails" in monitor_types:
#             tasks.append(self.run_powershell_script("alerts.ps1"))
#         results = await asyncio.gather(*tasks)
#         return results

#     async def stop_monitoring(self, monitor_type):
#         """Stop monitoring (files, folders, IPs, mails)."""
#         if monitor_type == "files":
#             output = await self.run_powershell_script("stop_monitor_files.ps1")
#         elif monitor_type == "folders":
#             output = await self.run_powershell_script("stop_monitor_folders.ps1")
#         elif monitor_type == "ips":
#             output = await self.run_powershell_script("stop_monitor_ips.ps1")
#         elif monitor_type == "emails":
#             output = await self.run_powershell_script("stop_monitor_emails.ps1")
#         else:
#             raise ValueError("Invalid monitor type")
#         return output


#---------------------------------------------------------
# OUPSSSSSSSSS

# API/app/services/monitor_service.py

import asyncio
import os
import logging
import psutil
import json
from configs.settings import Config

class MonitorService:
    def __init__(self):
        self.scripts_dir = os.path.join(Config.BASE_DIR, "Core", "scripts")
        self.status_file = os.path.join(Config.BASE_DIR, "Core", "data", "status.json")
        self.config_file = os.path.join(Config.BASE_DIR, "Core", "data", "config.json")
        logging.basicConfig(level=logging.INFO)

    def _read_config(self):
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _read_status(self):
        try:
            with open(self.status_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_status(self, data):
        try:
            with open(self.status_file, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error writing status: {e}")
            return False

    async def run_powershell_script(self, script_name, args=None):
        script_path = os.path.join(self.scripts_dir, script_name)
        command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]
        if args:
            command.extend(args)

        logging.info(f"Running script: {script_path}")
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode(), process.returncode, process.pid

    async def start_monitoring(self, monitor_types, intervals=None):
        config = self._read_config()
        results = {}

        script_map = {
            "files": "monitor_files.ps1",
            "folders": "monitor_folders.ps1",
            "ips": "monitor_ips.ps1",
            "emails": "alerts.ps1"
        }

        for monitor_type in monitor_types:
            if monitor_type not in script_map:
                results[monitor_type] = {"error": "Invalid monitor type"}
                continue

            script_name = script_map[monitor_type]
            args = []

            if monitor_type == "files":
                files = config.get("files", [])
                interval = intervals.get("files") if intervals else config.get("interval", 10)
                args = ["-FilesToMonitor", ",".join(files), "-Interval", str(interval)]

            elif monitor_type == "folders":
                folders = config.get("folders", [])
                interval = intervals.get("folders") if intervals else config.get("interval", 10)
                args = ["-FoldersToMonitor", ",".join(folders), "-Interval", str(interval)]

            elif monitor_type == "ips":
                ips = config.get("ips", [])
                interval = intervals.get("ips") if intervals else config.get("interval", 10)
                args = ["-IpsToMonitor", ",".join(ips), "-Interval", str(interval)]

            elif monitor_type == "emails":
                recipients = config.get("email", {}).get("recipients", [])
                interval = intervals.get("emails") if intervals else config.get("email", {}).get("interval", 3600)
                args = ["-EmailRecipients", ",".join(recipients), "-Interval", str(interval)]

            stdout, stderr, returncode, pid = await self.run_powershell_script(script_name, args)
            results[monitor_type] = {
                "stdout": stdout.strip(),
                "stderr": stderr.strip(),
                "returncode": returncode,
                "pid": pid
            }

        return results

    async def stop_monitoring(self, monitor_type):
        script_map = {
            "files": "monitor_files.ps1",
            "folders": "monitor_folders.ps1",
            "ips": "monitor_ips.ps1",
            "emails": "alerts.ps1"
        }

        if monitor_type not in script_map:
            return {"error": "Invalid monitor type"}, 400

        status_data = self._read_status()
        script_status = status_data.get(f"monitor_{monitor_type}", {})
        pid = script_status.get("PID")

        if not pid:
            return {"error": f"No PID found for {monitor_type}"}, 400

        try:
            process = psutil.Process(pid)
            process.terminate()
            # Manually update the status
            status_data[f"monitor_{monitor_type}"] = {"Status": "Stopped"}
            self._write_status(status_data)
            return {"message": f"{monitor_type} monitoring stopped successfully"}, 200
        except psutil.NoSuchProcess:
            return {"error": f"Process {pid} not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    async def stop_all_monitoring(self):
        status_data = self._read_status()
        script_map = {
            "files": "monitor_files.ps1",
            "folders": "monitor_folders.ps1",
            "ips": "monitor_ips.ps1",
            "emails": "alerts.ps1"
        }
        results = {}

        for monitor_type, script_name in script_map.items():
            entry = status_data.get(f"monitor_{monitor_type}", {})
            pid = entry.get("PID")

            if pid:
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    status_data[f"monitor_{monitor_type}"] = {"Status": "Stopped"}
                    results[monitor_type] = {"message": f"{monitor_type} monitoring stopped"}
                except psutil.NoSuchProcess:
                    results[monitor_type] = {"error": f"Process {pid} not found"}
                except Exception as e:
                    results[monitor_type] = {"error": str(e)}
            else:
                results[monitor_type] = {"message": f"{monitor_type} not running"}

        self._write_status(status_data)
        return results
