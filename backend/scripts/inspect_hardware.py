#!/usr/bin/env python3
"""
backend/scripts/inspect_hardware.py — Hardware Capacity & Resource Diagnostic Utility
Inspects CPU cores, system RAM, free disk space, and PyTorch acceleration capability.
Outputs structured summary for docs/LOCAL_ML_CAPACITY.md.
"""

import sys
import os
import platform
import shutil
import ctypes
import json
from pathlib import Path

def inspect_hardware():
    results = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "cpu_cores_logical": os.cpu_count(),
        "ram_gb_total": 0.0,
        "ram_gb_available": 0.0,
        "disk_gb_total": 0.0,
        "disk_gb_free": 0.0,
        "cuda_available": False,
        "torch_version": "N/A",
        "recommended_profile": "minimal_cpu"
    }

    try:
        import torch
        results["torch_version"] = torch.__version__
        results["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            results["gpu_name"] = torch.cuda.get_device_name(0)
            results["gpu_vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
    except ImportError:
        pass

    # Windows RAM via GlobalMemoryStatusEx
    if platform.system() == "Windows":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ('dwLength', ctypes.c_ulong),
                ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong),
                ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong),
                ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong),
                ('ullAvailVirtual', ctypes.c_ulonglong),
                ('sullAvailExtendedVirtual', ctypes.c_ulonglong),
            ]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            results["ram_gb_total"] = round(stat.ullTotalPhys / (1024**3), 2)
            results["ram_gb_available"] = round(stat.ullAvailPhys / (1024**3), 2)

    # Disk usage
    disk = shutil.disk_usage('.')
    results["disk_gb_total"] = round(disk.total / (1024**3), 2)
    results["disk_gb_free"] = round(disk.free / (1024**3), 2)

    # Determine recommended execution profile
    if results["cuda_available"] and results.get("gpu_vram_gb", 0) >= 4.0:
        results["recommended_profile"] = "gpu_accelerated"
    elif results["ram_gb_available"] >= 4.0 and results["disk_gb_free"] >= 20.0:
        results["recommended_profile"] = "balanced_cpu"
    else:
        results["recommended_profile"] = "minimal_cpu"

    print("=== INTELLIGRADE HARDWARE DIAGNOSTIC ===")
    print(f"Platform: {results['platform']}")
    print(f"Python: {results['python_version'].split()[0]}")
    print(f"CPU Logical Cores: {results['cpu_cores_logical']}")
    print(f"System RAM: {results['ram_gb_total']} GB Total | {results['ram_gb_available']} GB Available")
    print(f"Storage: {results['disk_gb_free']} GB Free of {results['disk_gb_total']} GB")
    print(f"PyTorch: {results['torch_version']} (CUDA: {results['cuda_available']})")
    print(f"Recommended Profile: {results['recommended_profile']}")
    print("========================================")

    return results

if __name__ == "__main__":
    inspect_hardware()
