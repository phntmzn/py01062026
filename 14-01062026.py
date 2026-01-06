#!/usr/bin/env python3
#
# Simple directory brute-force (dirsearch-style)
#
# Equivalent concept to:
#   dirsearch -u http://172.16.10.10:8081/
#

import requests
import time
from datetime import datetime

BASE_URL = "http://172.16.10.10:8081"
WORDLIST = [
    "upload",
    "uploads",
    "admin",
    "login",
    "images",
    "css",
]

TIMEOUT = 5

def now():
    return datetime.now().strftime("[%H:%M:%S]")

def main():
    print(f"Target: {BASE_URL}\n")
    print(f"{now()} Starting:")

    for word in WORDLIST:
        url = f"{BASE_URL}/{word}"

        try:
            r = requests.get(url, timeout=TIMEOUT, allow_redirects=False)
            size = len(r.content)

            if r.status_code == 200:
                print(
                    f"{now()} {r.status_code} - {size:>5}B  - /{word}"
                )

        except requests.exceptions.RequestException:
            pass

        # light delay to avoid hammering
        time.sleep(0.2)

if __name__ == "__main__":
    main()
