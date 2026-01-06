#!/usr/bin/env python3
"""
Linux OS detection script

Attempts to identify the Linux distribution by checking
standard files and commands.

Fails gracefully and returns meaningful exit codes.
"""

import os
import subprocess
import sys

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except (FileNotFoundError, PermissionError):
        return None

def detect_from_os_release():
    data = read_file("/etc/os-release")
    if not data:
        return None

    info = {}
    for line in data.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            info[key] = value.strip().strip('"')

    return info.get("PRETTY_NAME") or info.get("NAME")

def detect_from_lsb_release():
    try:
        result = subprocess.run(
            ["lsb_release", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.split(":", 1)[1].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None

def detect_from_legacy_files():
    checks = {
        "/etc/debian_version": "Debian-based",
        "/etc/redhat-release": "Red Hat-based",
        "/etc/arch-release": "Arch Linux",
        "/etc/gentoo-release": "Gentoo Linux",
        "/etc/alpine-release": "Alpine Linux"
    }

    for path, name in checks.items():
        if os.path.exists(path):
            content = read_file(path)
            return f"{name} ({content.strip() if content else 'unknown version'})"

    return None

def main():
    try:
        # 1) Ensure this is Linux
        if sys.platform != "linux":
            print("This system does not appear to be Linux.")
            sys.exit(2)

        # 2) Try modern method
        os_name = detect_from_os_release()
        if os_name:
            print(f"Detected OS: {os_name}")
            sys.exit(0)

        # 3) Try lsb_release
        os_name = detect_from_lsb_release()
        if os_name:
            print(f"Detected OS: {os_name}")
            sys.exit(0)

        # 4) Try legacy files
        os_name = detect_from_legacy_files()
        if os_name:
            print(f"Detected OS: {os_name}")
            sys.exit(0)

        # 5) Nothing worked
        print("Linux detected, but distribution could not be identified.")
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
