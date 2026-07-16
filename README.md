# daily-quotes-bot

A tiny, zero-server Telegram bot that sends you one quote per day — in order,
cycling back to the first after the last. No hosting, no database, no always-on
process: a scheduled [GitHub Actions](https://docs.github.com/en/actions)
workflow wakes up once a day, picks the quote for today, and sends it through
the Telegram Bot API. It runs comfortably inside the free tier.

> Want your own? Fork this repo, drop in your quotes, add two secrets, done.

## How it works

- `quotes.json` — your list of quotes, one string per entry.
- `send_quote.py` — computes today's quote as `days_since(ANCHOR_DATE) % len(quotes)`
  and sends it. Pure standard library, no dependencies.
- `.github/workflows/daily-quote.yml` — a `cron` schedule that runs the script
  once a day and injects your token and chat id from repository secrets.

Because the quote is derived from the date, there's no state to store: every run
is independent and idempotent, and the sequence stays in step even if a run is
missed.

## Setup (about 5 minutes)

### 1. Create your bot

1. In Telegram, open [@BotFather](https://t.me/BotFather) and send `/newbot`.
2. Choose a name and a username ending in `bot`.
3. Copy the **token** it gives you (looks like `1234567890:AAE...`).

### 2. Find your chat id

1. Open your new bot and send it any message (e.g. `/start`).
2. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser.
3. Copy the number in `"chat":{"id":...}` — that's your chat id.

### 3. Add the secrets

In your fork: **Settings → Secrets and variables → Actions → New repository secret**.
Add two:

| Name | Value |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | the token from BotFather |
| `TELEGRAM_CHAT_ID` | your chat id |

Secrets are encrypted and are **not** exposed to pull requests from forks, so a
public repo is safe.

### 4. Turn it on

Enable Actions for the repo (**Actions** tab → enable workflows), then trigger a
test run: **Actions → Daily quote → Run workflow**. You should get a message
within a few seconds. After that it runs automatically on the schedule.

## Customizing

- **Your own quotes:** edit `quotes.json`. Any length works; the cycle adapts.
- **The time of day:** edit the `cron` line in the workflow. It's in **UTC**.
  `0 8 * * *` is 10:00 in Warsaw during summer (CEST) and 09:00 in winter (CET).
  GitHub's scheduler is best-effort and can run a few minutes late.
- **Which quote lands when:** change `ANCHOR_DATE` in `send_quote.py`. On that
  date the first quote is sent, and the sequence counts forward from there.

## Run it locally

```bash
export TELEGRAM_BOT_TOKEN="123:abc"
export TELEGRAM_CHAT_ID="123456789"
python3 send_quote.py
```

## A note on scheduled workflows

GitHub disables scheduled workflows in a repository after **60 days of no
activity** and emails you a one-click link to re-enable them. If you'd rather it
never pause, push an occasional commit — or add a step that pings the repo — to
keep it "active."

## License

MIT — do whatever you like.
