#!/usr/bin/env python3
#
# Equivalent to:
#   nc 172.16.10.11 -v 21
#

import subprocess

HOST = "172.16.10.11"
PORT = "21"

def main():
    cmd = ["nc", "-v", HOST, PORT]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )

        # nc sends banner info to stdout, verbose info to stderr
        if result.stderr:
            print(result.stderr.strip())

        if result.stdout:
            print(result.stdout.strip())

    except subprocess.TimeoutExpired:
        print("[!] Connection timed out")
    except FileNotFoundError:
        print("[!] nc (netcat) not found on system")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
