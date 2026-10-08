# Retail Angle

A influencer accountability tracker. It logs explicit buy/sell stock callouts made by finance influencers on Reddit and Instagram, records the date and the influencer's claimed performance, then scores every call against the market over time. Claims get checked. Deleted losers stay on the record.

## How it works

1. **Ingest** — A scheduled poller reads public posts from a watchlist of investing subreddits via Reddit's official Data API. Instagram callouts are logged manually (post URL + screenshot), since Instagram offers no API path for reading arbitrary creators' posts.
2. **Ledger** — Every explicit buy/sell callout becomes one immutable row: influencer, ticker, direction, date, post URL, reasoning, and the influencer's claimed return. Nothing is deleted; removed posts are marked as removed.
3. **Score** — A nightly job computes each call's return vs. SPY and its sector ETF over 5/20/60-day windows, then rolls up per-influencer hit rate, average excess return, and claimed-vs-realized gap. Influencers need 10+ scored calls before appearing on the leaderboard.
4. **Cross-reference** — Callouts are joined against SEC Form 4 open-market insider transactions and 13F institutional holdings changes for confirmation/contradiction flags.

## Status

In development. Current pieces: Reddit poller (`reddit_poller.py`), database schema (`schema.sql`).

## Data sources

- Reddit Data API (official, OAuth, read-only)
- Instagram (manual intake)
- SEC EDGAR (Form 4, 13F — free)
- Stooq (free price history)

## Disclaimer

This is a research and track-record tool, not financial advice. Scores describe past callouts, not future performance. Not affiliated with Reddit, Instagram, or the SEC.
