#!/usr/bin/env python3
#
# Equivalent to:
#   nc 172.16.10.11 -v 21
#

import socket

HOST = "172.16.10.11"
PORT = 21
TIMEOUT = 5  # seconds

def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)

            print(f"[*] Connecting to {HOST}:{PORT}")
            sock.connect((HOST, PORT))

            # Receive banner
            banner = sock.recv(4096)

            if banner:
                print(banner.decode(errors="ignore").strip())
            else:
                print("[!] No banner received")

    except socket.timeout:
        print("[!] Connection timed out")
    except ConnectionRefusedError:
        print("[!] Connection refused")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
