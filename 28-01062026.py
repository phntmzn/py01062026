#!/usr/bin/env python3
"""
Reconstruct hex-encoded DNS exfil data from DNSChef logs (defensive/forensics).

Assumptions:
- Queries look like: <hexchunk>.blackhatbash.com
- Chunks are hex strings (0-9a-f) and should be concatenated in observed order.
- Output is decoded bytes (often ASCII text like /etc/passwd).

Usage:
  python3 reconstruct_dns_exfil.py dnschef.log --domain blackhatbash.com --out recovered.bin
  python3 reconstruct_dns_exfil.py dnschef.log --domain blackhatbash.com --print
"""

from __future__ import annotations
import argparse
import binascii
import re
from pathlib import Path
from typing import Iterable, List, Tuple


HEX_LABEL_RE = re.compile(r"^(?P<label>[0-9a-fA-F]+)\.(?P<domain>.+)$")


def iter_hex_labels_from_log(lines: Iterable[str], target_domain: str) -> List[str]:
    """
    Extract hex labels from lines that contain '<hex>.<target_domain>'.
    Works with typical DNSChef log lines that include the queried name.
    """
    labels: List[str] = []
    target_domain = target_domain.strip(".").lower()

    for line in lines:
        # Find anything that looks like "<something>.<domain>" in the line
        # We'll scan tokens to avoid overfitting to one log format.
        for token in re.split(r"[\s\]\[()\"',]+", line):
            token = token.strip().rstrip(".")
            if not token:
                continue

            m = HEX_LABEL_RE.match(token)
            if not m:
                continue

            label = m.group("label")
            domain = m.group("domain").strip(".").lower()

            if domain == target_domain and all(c in "0123456789abcdefABCDEF" for c in label):
                labels.append(label)

    return labels


def decode_hex_stream(labels: List[str]) -> bytes:
    """
    Concatenate hex labels and decode.
    Handles odd-length fragments by buffering.
    """
    hex_stream = "".join(labels)
    # If odd length, drop last nibble (or you could buffer/warn)
    if len(hex_stream) % 2 != 0:
        hex_stream = hex_stream[:-1]

    try:
        return binascii.unhexlify(hex_stream)
    except binascii.Error as e:
        raise ValueError(f"Failed to decode hex stream: {e}") from e


def main() -> None:
    ap = argparse.ArgumentParser(description="Reconstruct hex DNS exfil data from DNSChef logs.")
    ap.add_argument("logfile", type=Path, help="Path to dnschef.log (or similar DNS query log)")
    ap.add_argument("--domain", required=True, help="Exfil domain (e.g., blackhatbash.com)")
    ap.add_argument("--out", type=Path, default=None, help="Write recovered bytes to a file")
    ap.add_argument("--print", dest="do_print", action="store_true", help="Print recovered text (utf-8 with replacement)")
    ap.add_argument("--stats", action="store_true", help="Print basic suspiciousness stats (label length, count)")
    args = ap.parse_args()

    lines = args.logfile.read_text(errors="replace").splitlines()
    labels = iter_hex_labels_from_log(lines, args.domain)

    if not labels:
        raise SystemExit(f"No hex labels found for domain '{args.domain}' in {args.logfile}")

    recovered = decode_hex_stream(labels)

    if args.stats:
        lengths = [len(l) for l in labels]
        print(f"Found {len(labels)} chunks for {args.domain}")
        print(f"Min/avg/max chunk length: {min(lengths)}/{sum(lengths)/len(lengths):.1f}/{max(lengths)}")
        print(f"Recovered bytes: {len(recovered)}")

    if args.out:
        args.out.write_bytes(recovered)
        print(f"Wrote recovered bytes to: {args.out}")

    if args.do_print:
        print(recovered.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    main()
