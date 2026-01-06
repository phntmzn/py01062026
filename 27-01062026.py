#!/usr/bin/env python3
"""
Defensive exfiltration indicator detector (offline analysis).

Reads outbound connection logs and flags patterns associated with
covert exfiltration without sending any data.
"""

import csv
import sys
from collections import defaultdict
from statistics import mean, stdev

SMALL_BYTES_THRESHOLD = 1024        # small transfers
PERIODICITY_TOLERANCE_SEC = 10      # near-regular intervals
RARE_DEST_THRESHOLD = 3             # few unique sources contacting a dest

def parse_iso(ts):
    from datetime import datetime
    return datetime.fromisoformat(ts)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <outbound_logs.csv>")
        sys.exit(1)

    path = sys.argv[1]

    events = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["bytes_out"] = int(r["bytes_out"])
            r["timestamp"] = parse_iso(r["timestamp"])
            events.append(r)

    # Group by (src_ip, dst_ip, dst_port)
    groups = defaultdict(list)
    for e in events:
        key = (e["src_ip"], e["dst_ip"], e["dst_port"])
        groups[key].append(e)

    alerts = []

    # Rarity analysis: how many sources talk to each destination?
    dest_sources = defaultdict(set)
    for e in events:
        dest_sources[(e["dst_ip"], e["dst_port"])].add(e["src_ip"])

    for (src, dst, port), evs in groups.items():
        evs.sort(key=lambda x: x["timestamp"])

        # Indicator 1: many small transfers
        small_ratio = sum(1 for e in evs if e["bytes_out"] <= SMALL_BYTES_THRESHOLD) / len(evs)

        # Indicator 2: periodic timing
        intervals = [
            (evs[i]["timestamp"] - evs[i-1]["timestamp"]).total_seconds()
            for i in range(1, len(evs))
        ]
        periodic = False
        if len(intervals) >= 3:
            try:
                periodic = stdev(intervals) <= PERIODICITY_TOLERANCE_SEC
            except StatisticsError:
                periodic = False

        # Indicator 3: rare destination
        rare_dest = len(dest_sources[(dst, port)]) <= RARE_DEST_THRESHOLD

        score = 0
        score += 1 if small_ratio >= 0.7 else 0
        score += 1 if periodic else 0
        score += 1 if rare_dest else 0

        if score >= 2:
            alerts.append({
                "src": src,
                "dst": dst,
                "port": port,
                "events": len(evs),
                "small_ratio": round(small_ratio, 2),
                "periodic": periodic,
                "rare_destination": rare_dest,
                "score": score
            })

    if not alerts:
        print("No strong exfiltration indicators detected.")
        sys.exit(0)

    print("Potential exfiltration indicators:")
    for a in alerts:
        print(
            f"- {a['src']} -> {a['dst']}:{a['port']} | "
            f"events={a['events']} small_ratio={a['small_ratio']} "
            f"periodic={a['periodic']} rare_dest={a['rare_destination']} score={a['score']}"
        )

if __name__ == "__main__":
    main()
