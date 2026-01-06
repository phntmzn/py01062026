#!/usr/bin/env python3
"""
Equivalent of nmap_to_portfiles.sh

Logic:
1) Run: nmap -iL HOSTS_FILE --open
2) When a new host appears, remember its IP
3) For each open TCP port, append the IP to port-<port>.txt
"""

import subprocess
import sys
from pathlib import Path

HOSTS_FILE = "172-16-10-hosts.txt"

def main():
    if not Path(HOSTS_FILE).is_file():
        print(f"[!] Hosts file not found: {HOSTS_FILE}")
        sys.exit(1)

    # Run nmap and capture stdout
    cmd = ["nmap", "-iL", HOSTS_FILE, "--open"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    current_ip = None

    # Read output line by line (same idea as `while read -r line`)
    for line in proc.stdout:
        line = line.strip()

        # 2. Match: "Nmap scan report for <ip>"
        if line.startswith("Nmap scan report for"):
            current_ip = line.split("for", 1)[1].strip()

        # 3.  Match open TCP ports (e.g. "22/tcp open ssh")
        elif "tcp" in line and "open" in line and current_ip:
            port = line.split("/", 1)[0]
            filename = f"port-{port}.txt"

            # 5. Append IP to port file
            with open(filename, "a") as f:
                f.write(current_ip + "\n")

    proc.wait()

    if proc.returncode != 0:
        err = proc.stderr.read()
        print(f"[!] nmap error:\n{err}")
        sys.exit(1)

    print("[✓] Port files generated")

if __name__ == "__main__":
    main()
