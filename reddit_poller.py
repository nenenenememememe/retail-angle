"""Retail Angle — Reddit poller (read-only).

Polls a watchlist of subreddits and usernames via Reddit's official Data API
(application-only OAuth) and prints posts that look like explicit buy/sell
stock callouts. Review output before inserting anything into the ledger —
this script never writes to the database on its own.

Setup:
    cp .env.example .env   # then fill in your credentials
    pip install -r requirements.txt
    python reddit_poller.py
"""

import base64
import os
import re
import time

import requests

# --- config (edit me) -------------------------------------------------------
WATCH_SUBREDDITS = ["stocks", "wallstreetbets", "investing"]
WATCH_USERS: list[str] = []  # e.g. ["somefinfluencer"]
POST_LIMIT = 25
# ----------------------------------------------------------------------------

TICKER_RE = re.compile(r"\$([A-Z]{1,5})\b")
BUY_WORDS = re.compile(r"\b(buy|buying|bought|long|bullish|calls?)\b", re.I)
SELL_WORDS = re.compile(r"\b(sell|selling|sold|short|bearish|puts?)\b", re.I)

CID = os.environ["REDDIT_CLIENT_ID"]
SECRET = os.environ["REDDIT_CLIENT_SECRET"]
UA = os.environ.get(
    "REDDIT_USER_AGENT",
    "linux:com.retailangle.poll:v1.0 (by /u/placeholder)",
)


def get_token() -> tuple[str, float]:
    auth = base64.b64encode(f"{CID}:{SECRET}".encode()).decode()
    r = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        headers={"Authorization": f"Basic {auth}", "User-Agent": UA},
        data={"grant_type": "client_credentials"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"], time.time() + 3500


_token, _exp = get_token()


def api(path: str, params: dict | None = None) -> dict:
    global _token, _exp
    if time.time() > _exp:
        _token, _exp = get_token()
    r = requests.get(
        f"https://oauth.reddit.com{path}",
        headers={"Authorization": f"Bearer {_token}", "User-Agent": UA},
        params=params,
        timeout=15,
    )
    # respect rate limits; back off if Reddit says slow down
    remaining = r.headers.get("x-ratelimit-remaining")
    if remaining is not None and float(remaining) < 5:
        time.sleep(float(r.headers.get("x-ratelimit-reset", 60)))
    r.raise_for_status()
    return r.json()


def classify(title: str, body: str) -> str | None:
    text = f"{title} {body}"
    if not TICKER_RE.search(text):
        return None
    if BUY_WORDS.search(text) and not SELL_WORDS.search(text):
        return "BUY"
    if SELL_WORDS.search(text) and not BUY_WORDS.search(text):
        return "SELL"
    return None


def handle_post(p: dict) -> None:
    d = p["data"]
    direction = classify(d.get("title", ""), d.get("selftext", ""))
    if not direction:
        return
    tickers = sorted(set(TICKER_RE.findall(d.get("title", "") + " " + d.get("selftext", ""))))
    print(f"[{direction}] {'/'.join('$' + t for t in tickers)} "
          f"by u/{d['author']} on {time.strftime('%Y-%m-%d', time.gmtime(d['created_utc']))}")
    print(f"    {d['title'][:120]}")
    print(f"    https://reddit.com{d['permalink']}\n")


def main() -> None:
    for sub in WATCH_SUBREDDITS:
        data = api(f"/r/{sub}/new", {"limit": POST_LIMIT})
        for p in data["data"]["children"]:
            handle_post(p)
        time.sleep(2)  # stay comfortably under rate limits
    for user in WATCH_USERS:
        data = api(f"/user/{user}/submitted", {"limit": POST_LIMIT})
        for p in data["data"]["children"]:
            handle_post(p)
        time.sleep(2)


if __name__ == "__main__":
    main()
