#!/usr/bin/env python3
"""Check Claude service status.

This script is intentionally separate from the daily quote system.

It checks:
    https://status.claude.com/api/v2/summary.json

If Claude is operational, it tells GitHub Actions that the monitor
can be disabled.

If Claude is not operational, it sends the current status to Telegram.
"""

import json
import os
import sys
import urllib.parse
import urllib.request


CLAUDE_STATUS_URL = "https://status.claude.com/api/v2/summary.json"


def check_claude_status():
    request = urllib.request.Request(
        CLAUDE_STATUS_URL,
        headers={"User-Agent": "claude-monitor-github-action"},
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)

    status = payload.get("status", {})

    indicator = status.get("indicator", "unknown")
    description = status.get("description", "Unknown")

    return indicator, description


def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
        }
    ).encode()

    with urllib.request.urlopen(url, data=data, timeout=30) as response:
        payload = json.load(response)

    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API error: {payload}")


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise SystemExit(
            "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables."
        )

    try:
        indicator, description = check_claude_status()
    except Exception as exc:
        print(f"Could not check Claude status: {exc}")

        # Do not disable the monitor if the status API itself is unavailable.
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write("operational=false\n")

        return

    print(f"Claude status: {indicator} - {description}")

    if indicator == "operational":
        send_telegram(
            token,
            chat_id,
            "✅ Claude is back\n\n"
            "Claude is operational again.\n"
            "Claude monitoring will now stop.",
        )

        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write("operational=true\n")

        return

    send_telegram(
        token,
        chat_id,
        "⚠️ Claude Status\n\n"
        f"Status: {description}\n"
        f"Indicator: {indicator}\n\n"
        "Monitoring continues every 5 minutes.\n"
        "https://status.claude.com/",
    )

    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write("operational=false\n")


if __name__ == "__main__":
    sys.exit(main())