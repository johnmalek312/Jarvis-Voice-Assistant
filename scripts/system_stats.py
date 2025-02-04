import psutil
import platform
from GPUtil import getGPUs
from datetime import datetime
import subprocess
from tool_registry import register_tool

@register_tool()
def get_system_info():
    """
    Retrieves comprehensive system information, including operating system details and hardware specifications.
    Returns:
        dict: A dictionary containing the following system information:
            - System (str): The name of the operating system (e.g., 'Windows').
            - Node Name (str): The network name of the machine.
            - Release (str): The operating system release version.
            - Version (str): The detailed version of the operating system.
            - Machine (str): The machine type (e.g., 'AMD64').
            - CPU (str): The CPU model name.
            - Processor (str): The processor family type.
            - Boot Time (str): The system's boot time formatted as 'YYYY-MM-DD HH:MM:SS'.
            - Windows Edition (str): The specific edition of Windows (e.g., 'Windows 10 Pro') or 'Unknown' if not determined.
        str: An error message describing the exception if one occurs during information retrieval.
    """
    """Returns basic system information, including Windows edition."""
    try:
        windows_edition = "Unknown"
        if platform.system() == "Windows":
            output = subprocess.check_output("wmic os get caption", shell=True, text=True)
            windows_edition = list(filter(bool, output.strip().split("\n")))[1].strip()
        cpu_name = str(subprocess.check_output("wmic cpu get name", shell=True)).split("\\n")[1].strip()

        info = {
            "System": platform.system(),
            "Node Name": platform.node(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "CPU": cpu_name,
            "Processor": platform.processor(),
            "Boot Time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "Windows Edition": windows_edition,
        }
        return info
    except Exception as e:
        return str(e)

@register_tool()
def get_cpu_info():
    """Returns CPU usage and core details."""
    try:
        cpu_name = subprocess.check_output("wmic cpu get name", shell=True).decode().strip().split("\n")[1]
        print(cpu_name)
        cpu_info = {
            "CPU Name": cpu_name,
            "Physical Cores": psutil.cpu_count(logical=False),
            "Logical Cores": psutil.cpu_count(logical=True),
            "CPU Usage (%)": psutil.cpu_percent(interval=1),
            "CPU Frequency (MHz)": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        }
        return cpu_info
    except Exception as e:
        return str(e)

@register_tool()
def get_memory_info():
    """Returns memory usage details."""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        memory_info = {
            "Total Memory (GB)": round(memory.total / (1024 ** 3), 2),
            "Available Memory (GB)": round(memory.available / (1024 ** 3), 2),
            "Used Memory (GB)": round(memory.used / (1024 ** 3), 2),
            "Memory Usage (%)": memory.percent,
            "Total Swap (GB)": round(swap.total / (1024 ** 3), 2),
            "Used Swap (GB)": round(swap.used / (1024 ** 3), 2),
            "Swap Usage (%)": swap.percent,
        }
        return memory_info
    except Exception as e:
        return str(e)

@register_tool()
def get_disk_info():
    """Returns disk usage, I/O statistics, and percentages."""
    try:
        partitions = psutil.disk_partitions()
        disk_info = {}
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    "Total (GB)": round(usage.total / (1024 ** 3), 2),
                    "Used (GB)": round(usage.used / (1024 ** 3), 2),
                    "Free (GB)": round(usage.free / (1024 ** 3), 2),
                    "Usage (%)": usage.percent,
                }
            except PermissionError:
                continue

        io_counters = psutil.disk_io_counters()
        disk_io_info = {
            "Read (MB)": round(io_counters.read_bytes / (1024 ** 2), 2),
            "Write (MB)": round(io_counters.write_bytes / (1024 ** 2), 2),
            "Read Count": io_counters.read_count,
            "Write Count": io_counters.write_count,
        }

        return {"Disk Usage": disk_info, "Disk I/O": disk_io_info}
    except Exception as e:
        return str(e)

@register_tool()
def get_gpu_info():
    """Returns GPU details."""
    try:
        gpus = getGPUs()
        gpu_info = []
        for gpu in gpus:
            gpu_info.append({
                "GPU Name": gpu.name,
                "GPU Load (%)": gpu.load * 100,
                "GPU Memory Total (MB)": gpu.memoryTotal,
                "GPU Memory Used (MB)": gpu.memoryUsed,
                "GPU Memory Free (MB)": gpu.memoryFree,
                "Driver Version": gpu.driver,
            })
        return gpu_info
    except Exception as e:
        return str(e)

@register_tool()
def get_battery_info():
    """Returns battery status and percentage."""
    try:
        battery = psutil.sensors_battery()
        if not battery:
            return {"Battery": "No battery detected"}
        return {
            "Battery Percentage": battery.percent,
            "Charging": battery.power_plugged,
            "Time Left (hh:mm)": f"{battery.secsleft // 3600}:{(battery.secsleft % 3600) // 60}" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited",
        }
    except Exception as e:
        return str(e)

@register_tool()
def get_wifi_info():
    """Returns Wi-Fi information (Windows-only)."""
    try:
        wifi_info = []
        if platform.system() == "Windows":
            output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
            for line in output.split("\n"):
                if "SSID" in line and "BSSID" not in line:
                    wifi_info.append(line.split(":")[1].strip())
                if "Signal" in line:
                    wifi_info.append(f"Signal Strength: {line.split(':')[1].strip()}")
        return {"Wi-Fi": wifi_info or "No Wi-Fi detected"}
    except Exception as e:
        return str(e)
