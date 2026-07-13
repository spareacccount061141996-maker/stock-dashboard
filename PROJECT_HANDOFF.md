# Stock Dashboard Project Handoff

Last updated: 2026-07-13

This file is a compact backup of the working context between Vitrag and the agentic coding assistant. It is meant to let a future agent, model, or laptop pick up the project without needing the original chat history.

## Project Identity

Repository folder:

```text
C:\Users\Vitrag\Documents\Stock dash board
```

GitHub repository:

```text
https://github.com/spareacccount061141996-maker/stock-dashboard
```

Main deployed Streamlit URL:

```text
https://stock-dashboard-hedlfucmgdfondjkvaiwg7.streamlit.app/
```

Primary app file:

```text
app.py
```

Current branch:

```text
main
```

## What This App Is

This is a Streamlit dashboard for Indian market research, originally built around a conservative cash-secured put options strategy for NSE F&O stocks.

The app currently does these things:

- Screens a hardcoded universe of about 150+ Indian F&O stocks.
- Fetches stock data with `yfinance`.
- Shows CMP, sector, industry, analyst consensus target, upside %, beta, and company summaries.
- Estimates put strikes around 0.15 and 0.30 delta using Black-Scholes-Merton.
- Fetches next stock expiries using Zerodha Kite's public instruments master, using RELIANCE as the proxy stock.
- Provides forecast-source links such as Yahoo, TradingView, Investing India, MarketScreener, and Refinitiv/LSEG search context.
- Shows a Deep Dive & News tab with selected-stock news.
- Shows an Open IPOs tab with GMP data, subscription dates, IPO links, AI research links, and alert flags.
- Sends Telegram mobile alerts for IPO GMP threshold events through GitHub Actions.
- Has a keep-awake GitHub Action to ping Streamlit Cloud.

This is an educational/research tool only. It is not financial advice and should not place trades automatically.

## Current Technology Stack

Runtime and dependencies are pinned in `requirements.txt`:

```text
streamlit==1.59.1
yfinance==1.5.1
pandas==3.0.3
numpy==2.5.1
requests==2.34.2
beautifulsoup4==4.15.0
```

Python hints are present:

```text
runtime.txt      -> python-3.11
.python-version -> 3.11
```

Important deployment note:

Streamlit Cloud was observed to use Python `3.14.6` despite `runtime.txt`. Earlier pins to older `streamlit/pandas/numpy` caused dependency build failures on Python 3.14, especially Pillow/zlib. The app was moved back to Python-3.14-compatible versions:

- `streamlit==1.59.1`
- `pandas==3.0.3`
- `numpy==2.5.1`
- `yfinance==1.5.1`

Do not casually downgrade these again unless you confirm Streamlit Cloud is actually using a compatible Python runtime.

## How To Run Locally

From PowerShell:

```powershell
cd "C:\Users\Vitrag\Documents\Stock dash board"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Generic:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Useful local checks:

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py ipo_notifications.py
.\.venv\Scripts\python.exe -c "from streamlit.testing.v1 import AppTest; at = AppTest.from_file('app.py'); at.run(timeout=90); print('exception_count', len(at.exception)); [print(e.value) for e in at.exception]"
```

## Git / Deployment Notes

Recent important commits:

```text
d98f103 Strengthen Streamlit keep-awake pings
a27de5f Add IPO alert test mode
1ab2d58 Add IPO mobile alerts
ec01ee5 Fix Streamlit Cloud Python 3.14 deploy
75154ee Pin stable Streamlit Cloud runtime
376c725 Added Dev Container Folder
920f4ce Show app errors inside dashboard
c62a471 Prevent provider errors from crashing tabs
45d90f3 Harden IPO date display
4319fc3 Show IPO subscription dates
daf79af Make Streamlit keep-awake workflow tolerant
878a7d3 Keep Streamlit app active
```

Deployment is via Streamlit Cloud from GitHub `main`. Pushing to `main` triggers redeploy.

## App Structure

Important files:

```text
app.py
ipo_notifications.py
requirements.txt
README.md
PROJECT_HANDOFF.md
.github/workflows/keep-streamlit-awake.yml
.github/workflows/ipo-mobile-alerts.yml
.streamlit/config.toml
```

Important app concepts in `app.py`:

- `FO_SYMBOLS`: hardcoded Indian F&O universe.
- `fetch_stock_snapshot`: fetches Yahoo/yfinance stock info and optional news.
- `fetch_universe_snapshots`: concurrent stock scan with timeout.
- `put_delta_bsm`: Black-Scholes-Merton put delta.
- `strike_for_put_delta`: solves approximate strike for 0.15 / 0.30 delta.
- `fetch_stock_expiry_dates`: loads Zerodha Kite public instrument dump.
- `next_stock_expiries_from_broker`: next expiries for RELIANCE proxy.
- `fetch_open_ipos`: loads IPOWatch GMP data.
- `enrich_ipo_frame`: adds IPO start/last dates, research notes, alert flags, AI research links.
- `render_shortlist_tab`: All Ideas view.
- `render_deep_dive_tab`: selected stock details and news.
- `render_ipo_tab`: IPO/GMP view.
- `render_guarded`: wraps tabs so provider errors do not crash the whole app.

## Current Dashboard Tabs

1. `All Ideas`

- Shows all selected F&O stocks, not only filtered shortlist.
- Mobile-friendly card view and desktop table view.
- Sortable via Streamlit table and card sort selector.
- Includes sector, industry, industry outlook, CMP, target, upside, beta, 0.15/0.30 delta strikes.

2. `Deep Dive & News`

- Select from all F&O stocks.
- Uses checkboxes and remembered session state.
- Fetches news only for selected stocks.

3. `Open IPOs`

- Fetches IPOWatch GMP page.
- Shows open IPOs, GMP, price band, listing estimate, subscription start/end dates, type, status, alert, details link, AI research link.
- Fallback list exists but may be stale.

## IPO Mobile Alerts

Implemented in:

```text
ipo_notifications.py
.github/workflows/ipo-mobile-alerts.yml
```

Rules:

- Mainboard IPO alert if estimated GMP/listing premium is `>= 10%`.
- SME IPO alert if estimated GMP/listing premium is `>= 25%`.

Notification method:

- Telegram bot via GitHub Actions.
- Runs independently of Streamlit Cloud. The Streamlit app being asleep should not block Telegram alerts.

GitHub Secrets required:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Bot created by user:

```text
t.me/Goodipobot
```

Chat IDs observed during setup:

```text
949703124
8376156430
```

The latest `/start` in setup was from:

```text
8376156430
```

Important security note:

The Telegram bot token was pasted into the chat during setup. It should be regenerated in BotFather with `/revoke` after everything works, then update the GitHub secret `TELEGRAM_BOT_TOKEN`.

Manual test:

1. GitHub repo -> Actions.
2. Select `IPO Mobile Alerts`.
3. Click `Run workflow`.
4. Keep `Send a Telegram test notification` as `true`.
5. Expected Telegram message:

```text
IPO alert test

Telegram mobile notifications are connected correctly.
```

The user confirmed the test notification was received.

## Keep Streamlit Awake

Implemented in:

```text
.github/workflows/keep-streamlit-awake.yml
```

Current behavior:

- Runs hourly: `17 * * * *`.
- Pings both:
  - `https://stock-dashboard-hedlfucmgdfondjkvaiwg7.streamlit.app/`
  - `https://stock-dashboard-hedlfucmgdfondjkvaiwg7.streamlit.app/_stcore/health`
- Uses no-cache header and browser-like user agent.
- Best-effort: exits successfully even if app does not respond, to avoid GitHub failure email spam.

Important limitation:

Streamlit Community Cloud can still sleep or hibernate by design. GitHub scheduled workflows can be delayed or skipped. If this remains unreliable, use UptimeRobot or cron-job.org to ping every 5 minutes. That is more reliable than GitHub Actions for uptime.

The IPO Telegram alert workflow does not need Streamlit to be awake.

## Known Issues / Fragile Areas

- Streamlit Cloud may ignore `runtime.txt`; do not assume Python 3.11.
- `yfinance` can fail, rate-limit, or return missing data for Indian tickers.
- Some Yahoo symbols may be unavailable or changed:
  - `GMRINFRA.NS`
  - `LTIM.NS`
  - `PEL.NS`
  - `TATAMOTORS.NS`
- IPOWatch scraping can break if the website structure changes or blocks GitHub Actions.
- IPO fallback data is likely stale and should be refreshed or removed later.
- GMP is unofficial grey market data and can change quickly.
- Forecast/target links are best-effort. Some external pages may be locked, renamed, or region-blocked.
- Zerodha Kite public instruments dump is used only for expiries, not live option premiums.
- Live option premium data likely requires authenticated broker APIs such as Kite/Dhan; no reliable no-login live Indian options premium API was found.

## Prior Research / Decisions

### Live Options Premiums

Checked Zerodha Kite:

- Public instruments dump contains contracts but `last_price = 0`.
- Live quote endpoint requires authentication.
- Dhan Option Chain API has useful data such as LTP, bid/ask, OI, IV, Greeks, but requires client ID and access token.

Conclusion:

Live call/put premium should be added later through an authenticated broker API.

### AI Report Generator Direction

The user wants a new future tab:

```text
The Final Stock Rating Comprehensive Report Generator
```

Original desired persona:

Senior Quantitative Equity Researcher for Indian stocks, combining:

- Fundamentals.
- NSE/BSE filings.
- Peer comparisons.
- Latest news.
- Analyst targets from at least 3-4 sources within the last 6 months.
- Internet sentiment from non-financial sources like Reddit, ValuePickr, Glassdoor, Quora.
- Risk assessment.
- Technical/valuation context.

Required report structure:

1. Business & Sector Overview.
2. Financial Analysis & Balance Sheet.
3. Detailed Growth Prospects.
4. Valuation & Peer Comparison.
5. Risk Assessment / Critical Eye.
6. Third-Party Sentiment & Internet Legitimacy.

Tone:

- Technical and witty.
- Markdown tables.
- Bold key takeaways.
- Explicit `Data Gap` flags when information is unavailable or contradictory.

### AI Provider Discussion

Gemini:

- Gemini API has rate limits by RPM/TPM/RPD.
- Google Search grounding exists.
- Free tier has limits and may use data for product improvement.
- User has experienced Gemini rate limits.

Perplexity:

- Good for current web research and citations.
- Paid, but strong fit for deep research.

OpenRouter:

- Free models can be used for synthesis but usually do not provide live web search.
- Dashboard would need to gather current source packs first.
- Candidate free models discussed:
  - Tencent Hy3 Free, strong candidate if available.
  - NVIDIA Nemotron 3 Ultra Free / Super Free, large context.
  - OpenAI gpt-oss-120b Free, fallback.
  - Gemma free models as fallback.
- Avoid tiny/coding-only models for final equity research reports.

Best MVP decision:

Use manual AI mode first.

Proposed manual architecture:

1. Dashboard gathers a current source pack for a selected stock.
2. Dashboard generates a strict prompt using the report structure.
3. User copies prompt into ChatGPT / Claude / Gemini / Perplexity web manually.
4. AI returns a strict JSON report.
5. User pastes/imports JSON back into dashboard.
6. Dashboard validates JSON.
7. Dashboard renders clean report view.
8. Dashboard exports HTML/PDF.
9. Dashboard archives report by stock and month.

This avoids API costs and rate limits now, while keeping a future API path open.

Future automated architecture:

- Replace manual step 3 with API provider call.
- Keep same JSON schema.
- Add provider switch:
  - Manual
  - OpenRouter
  - Gemini
  - Perplexity/Sonar
  - Other future provider

## Proposed JSON Schema For Future Report Import

Draft shape:

```json
{
  "stock": "TCS.NS",
  "company": "Tata Consultancy Services",
  "report_month": "2026-07",
  "rating": "Hold",
  "confidence": "Medium",
  "valuation_view": "Fairly Valued",
  "one_line_thesis": "Short summary of the investment view.",
  "sections": {
    "business_sector_overview": "Text",
    "financial_analysis_balance_sheet": "Text",
    "growth_prospects": "Text",
    "valuation_peer_comparison": "Text",
    "risk_assessment": "Text",
    "third_party_sentiment": "Text"
  },
  "peer_table": [
    {
      "company": "Infosys",
      "ticker": "INFY.NS",
      "pe": 28.4,
      "pb": 7.2,
      "ev_ebitda": 18.1
    }
  ],
  "analyst_targets": [
    {
      "source": "Yahoo Finance",
      "target": 4200,
      "date": "2026-07-01",
      "url": "https://..."
    }
  ],
  "source_links": [
    {
      "label": "Latest result filing",
      "url": "https://..."
    }
  ],
  "data_gaps": [
    "No verified target price source within the last 6 months."
  ]
}
```

## Future Stock Rating Report Tab Plan

Suggested tab name:

```text
Final Stock Rating
```

Suggested MVP features:

- Stock selector from `FO_SYMBOLS`.
- Button: `Build Source Pack`.
- Display:
  - Current price.
  - 1M/3M/6M/1Y returns vs Nifty or sector proxy if available.
  - yfinance financial metrics.
  - Peer list and peer valuation table.
  - Latest news links.
  - Forecast/target source links.
  - Sentiment links:
    - Reddit search.
    - ValuePickr search.
    - Glassdoor search.
    - Quora search.
  - Data gaps.
- Button: `Copy AI Prompt`.
- Text area: `Paste AI JSON Report`.
- Validate JSON against schema.
- Render report in dashboard.
- Export as:
  - HTML.
  - PDF.
- Archive under a local folder or Streamlit-compatible storage approach:

```text
reports/YYYY-MM/STOCK.json
reports/YYYY-MM/STOCK.html
reports/YYYY-MM/STOCK.pdf
```

Important: Streamlit Cloud local filesystem is ephemeral. For durable cloud archives, use GitHub commits, cloud storage, or downloadable exports. For MVP, manual download is acceptable.

## What The Next Agent Should Do First

1. Read this file.
2. Run:

```powershell
git status --short
git log --oneline -8
```

3. Check app still runs:

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py ipo_notifications.py
```

4. If editing app UI, avoid broad refactors. Keep changes scoped.
5. Do not downgrade `requirements.txt` without checking Streamlit Cloud logs.
6. If touching Telegram notifications, preserve test mode.
7. If adding report generator, use manual JSON import/export first.

## User Preferences Learned

- Wants practical MVP first, polish later.
- Strong preference for useful mobile experience.
- Wants all F&O stocks visible by default, not only filtered shortlist.
- Wants low-cost/free solutions until the project earns money.
- Is open to paid providers later if value is proven.
- Wants source-backed stock research, not stale model memory.
- Cares about latest data and latest news.
- Wants report outputs in HTML/PDF eventually.
- Wants dashboard to be easy to continue across laptops/agents/models.

## Security Notes

- Never commit actual API keys or Telegram tokens.
- `.streamlit/secrets.toml` is ignored.
- `.notification-state/` is ignored.
- Telegram token was exposed in chat during setup; regenerate it through BotFather `/revoke` when convenient and update GitHub secret.

## Current Status

As of this handoff:

- Streamlit app works after Python 3.14 dependency correction.
- Telegram test notification was received successfully.
- IPO alerts are scheduled and independent of Streamlit sleep.
- Keep-awake workflow has been strengthened to hourly pings.
- Next major feature under discussion is the manual AI-assisted stock report generator.
