#!/usr/bin/env python3
"""Send the quote of the day to a Telegram chat.

The quote is chosen by cycling through quotes.json in order: the number of days
elapsed since ANCHOR_DATE, taken modulo the number of quotes. After the last
quote the cycle restarts at the first one.

Configuration comes from environment variables (set them as GitHub Actions
secrets, or export them locally):

    TELEGRAM_BOT_TOKEN   token from @BotFather
    TELEGRAM_CHAT_ID     your chat id (message the bot, then check getUpdates)
"""

import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

# Day 0 of the cycle: on this date quote #1 is sent. Change if you want to
# re-anchor which quote lands on a given day.
ANCHOR_DATE = dt.date(2026, 7, 15)

HERE = os.path.dirname(os.path.abspath(__file__))


def load_quotes():
    with open(os.path.join(HERE, "quotes.json"), encoding="utf-8") as f:
        quotes = json.load(f)
    if not quotes:
        raise SystemExit("quotes.json is empty")
    return quotes


def quote_for(today, quotes):
    index = (today - ANCHOR_DATE).days % len(quotes)
    return index, quotes[index]


def send(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    with urllib.request.urlopen(url, data=data, timeout=30) as resp:
        payload = json.load(resp)
    if not payload.get("ok"):
        raise SystemExit(f"Telegram API error: {payload}")
    return payload


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit(
            "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables."
        )

    quotes = load_quotes()
    today = dt.datetime.now(dt.timezone.utc).date()
    index, quote = quote_for(today, quotes)
    text = f"\U0001f33f {index + 1}/{len(quotes)}\n\n{quote}"

    send(token, chat_id, text)
    print(f"Sent quote {index + 1}/{len(quotes)}: {quote}")


if __name__ == "__main__":
    sys.exit(main())
