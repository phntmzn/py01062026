#!/usr/bin/env python3
#
# Python equivalent of curl_banner_grab.sh
#

import subprocess
import sys

DEFAULT_PORT = "80"

def main():
    # 1. Prompt for IP
    ip = input("Type a target IP address: ").strip()

    # 2. Prompt for port
    port = input(f"Type a target port (default: {DEFAULT_PORT}): ").strip()

    # 3. Validate IP
    if not ip:
        print("You must provide an IP address.")
        sys.exit(1)

    # 4-5. Default port handling
    if not port:
        print(f"You did not provide a specific port, defaulting to {DEFAULT_PORT}")
        port = DEFAULT_PORT

    print(f"Attempting to grab the Server header of {ip}...")

    # 6. Run curl and extract Server header
    cmd = ["curl", "-s", "--head", f"{ip}:{port}"]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            print(f"[!] curl error:\n{result.stderr.strip()}")
            sys.exit(1)

        server_header = None
        for line in result.stdout.splitlines():
            if line.lower().startswith("server:"):
                server_header = line.split(":", 1)[1].strip()
                break

        print(
            f"Server header for {ip} on port {port} is: "
            f"{server_header if server_header else 'Not found'}"
        )

    except subprocess.TimeoutExpired:
        print("[!] Connection timed out")
    except FileNotFoundError:
        print("[!] curl not found on system")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
