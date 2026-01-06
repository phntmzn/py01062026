#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path

# Absolute path to the kext
KEXT_PATH = Path("/Library/Extensions/MyDriver.kext")

def run(cmd):
    subprocess.run(cmd, check=True)

def require_root():
    if os.geteuid() != 0:
        print("This script must be run as root (use sudo).")
        sys.exit(1)

def validate_kext():
    if not KEXT_PATH.exists():
        print(f"Kext not found: {KEXT_PATH}")
        sys.exit(1)

def load_kext():
    validate_kext()
    run([
        "kmutil",
        "load",
        "-p", str(KEXT_PATH)
    ])
    print("Kext loaded")

def unload_kext():
    validate_kext()
    run([
        "kmutil",
        "unload",
        "-p", str(KEXT_PATH)
    ])
    print("Kext unloaded")

def status_kext():
    run(["kmutil", "showloaded"])

def usage():
    print("Usage:")
    print("  sudo python3 kext_control.py load")
    print("  sudo python3 kext_control.py unload")
    print("  sudo python3 kext_control.py status")

if __name__ == "__main__":
    require_root()

    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "load":
        load_kext()
    elif cmd == "unload":
        unload_kext()
    elif cmd == "status":
        status_kext()
    else:
        usage()
        sys.exit(1)
