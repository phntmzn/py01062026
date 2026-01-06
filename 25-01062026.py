#!/usr/bin/env python3
"""
Internal network probing with service mapping (Linux)

- Prioritizes commonly open ports
- Maps ports to service names via /etc/services
- Uses TCP connect scanning
- Fails gracefully
"""

import socket
import sys
from pathlib import Path

# Commonly open ports, ordered by frequency
PRIORITY_PORTS = [
    22,    # SSH
    80,    # HTTP
    443,   # HTTPS
    3389,  # RDP
    3306,  # MySQL
    445,   # SMB
    139,   # NetBIOS
    53,    # DNS
    25,    # SMTP
    21,    # FTP
]

TIMEOUT = 0.5

def load_services():
    services = {}
    path = Path("/etc/services")

    if not path.exists():
        return services

    try:
        for line in path.read_text().splitlines():
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            name = parts[0]
            port_proto = parts[1]

            if "/" in port_proto:
                port, proto = port_proto.split("/", 1)
                if proto == "tcp":
                    services[int(port)] = name
    except Exception:
        pass

    return services

def scan_port(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False

def main():
    try:
        if sys.platform != "linux":
            print("This script is intended for Linux systems.")
            sys.exit(2)

        network = input("Target network (example: 10.1.0.): ").strip()
        if not network.endswith("."):
            print("Network must end with a dot, e.g. 10.1.0.")
            sys.exit(1)

        services = load_services()
        partial = False

        print(f"\nProbing network {network}0/24\n")

        for host_id in range(1, 255):
            host = f"{network}{host_id}"
            found = False

            for port in PRIORITY_PORTS:
                if scan_port(host, port):
                    service = services.get(port, "unknown")
                    print(f"{host}:{port} ({service}) open")
                    found = True

            if found:
                print("-" * 40)

        sys.exit(0)

    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
