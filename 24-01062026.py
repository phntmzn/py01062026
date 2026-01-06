#!/usr/bin/env python3
"""
Block device discovery script (Linux)

Replicates:
- lsblk
- cat /proc/partitions

Fails gracefully if commands or files are unavailable.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None

def read_proc_partitions():
    path = Path("/proc/partitions")
    if not path.exists():
        return None
    try:
        return path.read_text().strip()
    except PermissionError:
        return None

def main():
    try:
        # 1) Ensure Linux
        if sys.platform != "linux":
            print("This script is intended for Linux systems only.")
            sys.exit(2)

        partial = False

        print("=== Block Devices (lsblk) ===")
        lsblk_output = run_command(["lsblk"])
        if lsblk_output:
            print(lsblk_output)
        else:
            print("lsblk unavailable")
            partial = True

        print("\n=== Kernel Partition Table (/proc/partitions) ===")
        proc_output = read_proc_partitions()
        if proc_output:
            print(proc_output)
        else:
            print("/proc/partitions unavailable")
            partial = True

        if partial:
            sys.exit(1)
        sys.exit(0)

    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
