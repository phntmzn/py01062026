#!/usr/bin/env python3

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
    outdir = Path(f"nmap_{target}_{timestamp}")
    outdir.mkdir(parents=True, exist_ok=True)

    output_base = outdir / "scan"

    print(f"[*] Running nmap -A scan against {target}")

    cmd = [
        "nmap",
        "-A",
        target,
        "-oA",
        str(output_base)
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
