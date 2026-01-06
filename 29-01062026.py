import json
import os
import urllib.request
import urllib.error

def send_slack_webhook(webhook_url: str, text: str, *, timeout: float = 5.0) -> None:
    """
    Send a plain-text Slack webhook message (legitimate notification use).
    """
    payload = {"text": text}
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if resp.status >= 300:
                raise RuntimeError(f"Slack webhook error HTTP {resp.status}: {body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to reach Slack webhook: {e}") from e


if __name__ == "__main__":
    # Best practice: store secrets in env vars, not in source code
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        raise SystemExit("Set SLACK_WEBHOOK_URL environment variable")

    send_slack_webhook(url, "✅ Scan completed: 12 hosts checked, 0 critical findings.")
