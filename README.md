# Cash-Secured Put Strategy Tracker

A Streamlit dashboard for screening Indian F&O stocks for a conservative cash-secured put strategy.

## Run

```powershell
pip install -r requirements.txt
streamlit run app.py
```

The app uses a hardcoded F&O universe, fetches market data and news from Yahoo Finance through `yfinance`, calculates analyst upside, estimates 0.15 and 0.30 delta put strike regions using the Black-Scholes-Merton formula, and provides a selectable forecast-source link for Yahoo Finance, TradingView, Investing India consensus estimates, MarketScreener, and Refinitiv/LSEG search context.

The first load scans the full hardcoded F&O universe by default. Remove stocks from the sidebar selector when you want a faster or narrower run, and use **Refresh Data** if Yahoo temporarily fails or stale cached results need to be cleared. The All Ideas tab shows every fetched stock by default; the upside filter is optional. Use Cards view on phone and Table view on desktop. The Deep Dive tab uses stock checkboxes and fetches news only for the checked names.

The app loads the next three RELIANCE NFO stock expiries from Zerodha Kite's public instruments master and uses the selected expiry as the date input for stock put-delta estimates. Stock monthly expiries are generally common across names, so Reliance is used as the proxy. If the broker instrument dump cannot be reached, the app clearly marks the expiry as unavailable and uses a 30-day fallback for the Black-Scholes delta strike estimates.

The Open IPOs tab attempts to fetch open IPO GMP data from IPOWatch and falls back to a curated current list if the source is blocked. It includes GMP, price band, estimated listing, IPO details links, an AI research link, and an alert flag for good/high GMP on the second-last subscription day.

## Mobile IPO Alerts

The repository includes an optional Telegram-based mobile alert workflow. It scans open IPOs on weekdays and sends a phone notification when:

- Mainboard IPO estimated GMP/listing premium is at least 10%.
- SME IPO estimated GMP/listing premium is at least 25%.

To enable it, create a Telegram bot with BotFather, send one message to the bot from your phone, then add these GitHub repository secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

The workflow can also be run manually from GitHub Actions under **IPO Mobile Alerts**.

This is an educational tool only. Always verify option prices, liquidity, lot size, margin, and tax treatment before placing trades.
