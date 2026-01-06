#!/usr/bin/env python3
"""
Educational example:
- Shards a file into N-line chunks
- Schedules local jobs at staggered times
- Processes shards locally (no network)
- Reassembles the file to verify integrity
"""

import os
import sys
import time
import threading
from pathlib import Path

LINES_PER_SHARD = 5
BASE_DELAY_SECONDS = 60  # 1 minute per shard index

def shard_file(src: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    shards = []

    with src.open("r", errors="ignore") as f:
        lines = []
        idx = 0
        for line in f:
            lines.append(line)
            if len(lines) == LINES_PER_SHARD:
                shard = out_dir / f"x{idx:02d}"
                shard.write_text("".join(lines))
                shards.append(shard)
                lines.clear()
                idx += 1
        if lines:
            shard = out_dir / f"x{idx:02d}"
            shard.write_text("".join(lines))
            shards.append(shard)

    return shards

def process_shard_later(shard: Path, delay: int, processed_dir: Path):
    def job():
        time.sleep(delay)
        processed_dir.mkdir(parents=True, exist_ok=True)
        # Local “processing” only: copy to processed_dir
        target = processed_dir / shard.name
        target.write_text(shard.read_text())
        print(f"Processed {shard.name} after {delay}s")

    t = threading.Thread(target=job, daemon=True)
    t.start()
    return t

def reassemble(processed_dir: Path, output: Path):
    parts = sorted(processed_dir.glob("x*"))
    with output.open("w") as out:
        for p in parts:
            out.write(p.read_text())

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <source_file>")
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        print("Source file not found.")
        sys.exit(1)

    work = Path("./work")
    shards_dir = work / "shards"
    processed_dir = work / "processed"
    output = work / "reassembled.txt"

    shards = shard_file(src, shards_dir)
    threads = []

    for shard in shards:
        idx = int(shard.name[1:])  # x00 -> 0
        delay = idx * BASE_DELAY_SECONDS
        threads.append(process_shard_later(shard, delay, processed_dir))

    # Wait long enough for all jobs (demo purposes)
    max_delay = (len(shards) - 1) * BASE_DELAY_SECONDS
    time.sleep(max_delay + 2)

    reassemble(processed_dir, output)
    print("Reassembled file written to:", output)

if __name__ == "__main__":
    main()
