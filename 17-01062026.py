#!/usr/bin/env python3
"""
Educational interface demonstrating:
- request flow
- response diffing
- returning only new output

This version DOES NOT exploit vulnerabilities.
"""

import requests
import urllib.parse
import difflib

def main():
    host = input("Host: ").strip()
    port = input("Port: ").strip()

    base_url = f"http://{host}:{port}"

    print("Type commands (benign input only). Ctrl+C to exit.")

    while True:
        try:
            raw_command = input("$ ").strip()
            encoded_command = urllib.parse.quote(raw_command)

            # 1) Fetch previous response snapshot
            prev_resp = requests.get(
                f"{base_url}/amount_to_donate.txt",
                timeout=5
            ).text.splitlines()

            # 2) Send a benign request (no injection)
            #    This simulates the interaction flow only
            requests.get(
                f"{base_url}/donate.php",
                params={"amount": encoded_command},
                timeout=5
            )

            # 3) Fetch new response snapshot
            new_resp = requests.get(
                f"{base_url}/amount_to_donate.txt",
                timeout=5
            ).text.splitlines()

            # 4) Compute delta (only newly added lines)
            diff = difflib.unified_diff(
                prev_resp,
                new_resp,
                lineterm=""
            )

            for line in diff:
                if line.startswith("+") and not line.startswith("+++"):
                    print(line[1:])

        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
