#!/usr/bin/env python3
"""
User session and login activity collection (Linux)

Wraps standard commands:
- w
- who
- last
- lastb (optional, requires elevated privileges)

Fails gracefully if files or commands are unavailable.
"""

import subprocess
import sys

def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

def main():
    try:
        # 1) Ensure Linux
        if sys.platform != "linux":
            print("This script is intended for Linux systems.")
            sys.exit(2)

        partial = False

        print("=== Current Logged-In Users (w) ===")
        output = run_command(["w"])
        if output:
            print(output)
        else:
            print("Unavailable")
            partial = True

        print("\n=== Current Sessions (who) ===")
        output = run_command(["who"])
        if output:
            print(output)
        else:
            print("Unavailable")
            partial = True

        print("\n=== Login History (last) ===")
        output = run_command(["last", "-n", "10"])
        if output:
            print(output)
        else:
            print("Unavailable")
            partial = True

        print("\n=== Failed Login Attempts (lastb) ===")
        output = run_command(["lastb", "-n", "10"])
        if output:
            print(output)
        else:
            print("Unavailable (may require root privileges)")
            partial = True

        if partial:
            sys.exit(1)
        sys.exit(0)

    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
