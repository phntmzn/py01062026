#!/usr/bin/env python3
#
# Make executable:
#   chmod +x syn_scan.py
#
# Run:
#   ./syn_scan.py 192.168.1.1
#
# NOTE:
# - Requires sudo/root privileges for SYN scans (-sS)
# - Only scan systems you own or have permission to test
#

import sys
import subprocess
from datetime import datetime
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <target>")
        sys.exit(1)

    target = sys.argv[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(f"nmap_syn_{target}_{timestamp}")
    outdir.mkdir(parents=True, exist_ok=True)

    output_base = outdir / "scan"

    print(f"[*] Running Nmap SYN scan (-sS) against {target}")
    print("[!] Requires sudo/root privileges")

    cmd = [
        "sudo", "nmap",
        "-sS",
        "-Pn",
        "-T4",
        target,
        "-oA", str(output_base)
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Scan failed: {e}")
        sys.exit(1)

    print("[✓] Scan complete")
    print("[*] Results saved to:")
    print(f"    {output_base}.nmap")
    print(f"    {output_base}.gnmap")
    print(f"    {output_base}.xml")

if __name__ == "__main__":
    main()
