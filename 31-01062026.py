#!/usr/bin/env python3
import argparse
import re
import sys
from email import policy
from email.parser import BytesParser
from urllib.parse import urlparse

SUSPICIOUS_WORDS = {
    "verify", "password", "login", "urgent", "invoice", "wire", "gift", "reset",
    "suspended", "security", "action required", "mfa", "2fa"
}

URL_RE = re.compile(r"https?://[^\s<>\"]+")

def extract_text_parts(msg):
    texts = []
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype in ("text/plain", "text/html"):
                try:
                    texts.append(part.get_content())
                except Exception:
                    pass
    else:
        try:
            texts.append(msg.get_content())
        except Exception:
            pass
    return "\n".join(texts)

def is_ip_host(host: str) -> bool:
    # naive IPv4 check
    return bool(re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", host))

def looks_like_punycode(host: str) -> bool:
    return host.lower().startswith("xn--")

def score_url(u: str) -> list[str]:
    reasons = []
    try:
        p = urlparse(u)
        host = (p.hostname or "").lower()
        if not host:
            return ["missing hostname"]
        if is_ip_host(host):
            reasons.append("URL host is an IP address")
        if looks_like_punycode(host):
            reasons.append("punycode/IDN hostname (possible look-alike)")
        if "@" in u.split("://", 1)[-1].split("/", 1)[0]:
            reasons.append("contains @ in authority (obfuscation)")
        if p.scheme not in ("http", "https"):
            reasons.append(f"non-http scheme: {p.scheme}")
        # suspicious paths
        path = (p.path or "").lower()
        if any(k in path for k in ("login", "signin", "verify", "password", "reset")):
            reasons.append("suspicious auth-related path keywords")
        # long subdomain chains
        if host.count(".") >= 4:
            reasons.append("many subdomain levels")
    except Exception as e:
        reasons.append(f"parse error: {e}")
    return reasons

def main():
    ap = argparse.ArgumentParser(description="Basic phishing triage for .eml files (defensive).")
    ap.add_argument("eml", help="Path to .eml file")
    args = ap.parse_args()

    with open(args.eml, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    frm = msg.get("From", "")
    subj = msg.get("Subject", "")
    reply_to = msg.get("Reply-To", "")
    to = msg.get("To", "")
    date = msg.get("Date", "")

    body = extract_text_parts(msg)
    body_l = body.lower()

    urls = sorted(set(URL_RE.findall(body)))

    print("=== Headers ===")
    print(f"From:     {frm}")
    print(f"To:       {to}")
    print(f"Subject:  {subj}")
    print(f"Date:     {date}")
    if reply_to:
        print(f"Reply-To: {reply_to}")

    print("\n=== Body keyword flags ===")
    hits = [w for w in SUSPICIOUS_WORDS if w in body_l]
    print("Matches:" if hits else "Matches: none")
    for w in hits:
        print(f"  - {w}")

    print("\n=== URLs ===")
    if not urls:
        print("No URLs found.")
        return

    for u in urls:
        reasons = score_url(u)
        if reasons:
            print(f"\n[u] {u}")
            for r in reasons:
                print(f"  ! {r}")
        else:
            print(f"\n[ ] {u} (no obvious red flags)")

if __name__ == "__main__":
    sys.exit(main() or 0)
