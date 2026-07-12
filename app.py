from __future__ import annotations

import math
import re
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import date, timedelta
from html import escape
from io import StringIO
from typing import Any
from urllib.parse import quote, quote_plus

import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from bs4 import BeautifulSoup


KITE_INSTRUMENTS_URL = "https://api.kite.trade/instruments"
IPOWATCH_GMP_URL = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"

FO_SYMBOLS = [
    "ABB.NS",
    "ACC.NS",
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "ALKEM.NS",
    "AMBUJACEM.NS",
    "APOLLOHOSP.NS",
    "APOLLOTYRE.NS",
    "ASHOKLEY.NS",
    "ASIANPAINT.NS",
    "ASTRAL.NS",
    "AUBANK.NS",
    "AUROPHARMA.NS",
    "AXISBANK.NS",
    "BAJAJ-AUTO.NS",
    "BAJAJFINSV.NS",
    "BAJFINANCE.NS",
    "BALKRISIND.NS",
    "BANDHANBNK.NS",
    "BANKBARODA.NS",
    "BATAINDIA.NS",
    "BEL.NS",
    "BERGEPAINT.NS",
    "BHARATFORG.NS",
    "BHARTIARTL.NS",
    "BHEL.NS",
    "BIOCON.NS",
    "BOSCHLTD.NS",
    "BPCL.NS",
    "BRITANNIA.NS",
    "BSOFT.NS",
    "CANBK.NS",
    "CHAMBLFERT.NS",
    "CHOLAFIN.NS",
    "CIPLA.NS",
    "COALINDIA.NS",
    "COFORGE.NS",
    "COLPAL.NS",
    "CONCOR.NS",
    "COROMANDEL.NS",
    "CROMPTON.NS",
    "CUB.NS",
    "CUMMINSIND.NS",
    "DABUR.NS",
    "DALBHARAT.NS",
    "DEEPAKNTR.NS",
    "DIVISLAB.NS",
    "DIXON.NS",
    "DLF.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "ESCORTS.NS",
    "EXIDEIND.NS",
    "FEDERALBNK.NS",
    "GAIL.NS",
    "GLENMARK.NS",
    "GMRINFRA.NS",
    "GNFC.NS",
    "GODREJCP.NS",
    "GODREJPROP.NS",
    "GRANULES.NS",
    "GRASIM.NS",
    "GUJGASLTD.NS",
    "HAL.NS",
    "HAVELLS.NS",
    "HCLTECH.NS",
    "HDFCAMC.NS",
    "HDFCBANK.NS",
    "HDFCLIFE.NS",
    "HEROMOTOCO.NS",
    "HINDALCO.NS",
    "HINDCOPPER.NS",
    "HINDPETRO.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "ICICIGI.NS",
    "ICICIPRULI.NS",
    "IDEA.NS",
    "IDFCFIRSTB.NS",
    "IEX.NS",
    "IGL.NS",
    "INDHOTEL.NS",
    "INDIACEM.NS",
    "INDIAMART.NS",
    "INDIGO.NS",
    "INDUSINDBK.NS",
    "INDUSTOWER.NS",
    "INFY.NS",
    "IOC.NS",
    "IPCALAB.NS",
    "IRCTC.NS",
    "ITC.NS",
    "JINDALSTEL.NS",
    "JKCEMENT.NS",
    "JSWSTEEL.NS",
    "JUBLFOOD.NS",
    "KOTAKBANK.NS",
    "LALPATHLAB.NS",
    "LAURUSLABS.NS",
    "LICHSGFIN.NS",
    "LT.NS",
    "LTIM.NS",
    "LTTS.NS",
    "LUPIN.NS",
    "M&M.NS",
    "M&MFIN.NS",
    "MANAPPURAM.NS",
    "MARICO.NS",
    "MARUTI.NS",
    "MCX.NS",
    "METROPOLIS.NS",
    "MFSL.NS",
    "MGL.NS",
    "MOTHERSON.NS",
    "MPHASIS.NS",
    "MRF.NS",
    "MUTHOOTFIN.NS",
    "NATIONALUM.NS",
    "NAUKRI.NS",
    "NAVINFLUOR.NS",
    "NESTLEIND.NS",
    "NMDC.NS",
    "NTPC.NS",
    "OBEROIRLTY.NS",
    "OFSS.NS",
    "ONGC.NS",
    "PAGEIND.NS",
    "PEL.NS",
    "PERSISTENT.NS",
    "PETRONET.NS",
    "PFC.NS",
    "PIDILITIND.NS",
    "PIIND.NS",
    "PNB.NS",
    "POLYCAB.NS",
    "POWERGRID.NS",
    "PVRINOX.NS",
    "RAMCOCEM.NS",
    "RBLBANK.NS",
    "RECLTD.NS",
    "RELIANCE.NS",
    "SAIL.NS",
    "SBICARD.NS",
    "SBILIFE.NS",
    "SBIN.NS",
    "SHREECEM.NS",
    "SHRIRAMFIN.NS",
    "SIEMENS.NS",
    "SRF.NS",
    "SUNPHARMA.NS",
    "SUNTV.NS",
    "SYNGENE.NS",
    "TATACHEM.NS",
    "TATACOMM.NS",
    "TATACONSUM.NS",
    "TATAMOTORS.NS",
    "TATAPOWER.NS",
    "TATASTEEL.NS",
    "TCS.NS",
    "TECHM.NS",
    "TITAN.NS",
    "TORNTPHARM.NS",
    "TRENT.NS",
    "TVSMOTOR.NS",
    "UBL.NS",
    "ULTRACEMCO.NS",
    "UPL.NS",
    "VEDL.NS",
    "VOLTAS.NS",
    "WIPRO.NS",
    "ZEEL.NS",
    "ZYDUSLIFE.NS",
]

DEFAULT_SCAN_SYMBOLS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "INFY.NS",
    "ITC.NS",
    "BHARTIARTL.NS",
    "HINDUNILVR.NS",
    "LT.NS",
    "SBIN.NS",
    "KOTAKBANK.NS",
    "AXISBANK.NS",
    "MARUTI.NS",
    "SUNPHARMA.NS",
    "TITAN.NS",
    "ASIANPAINT.NS",
    "ULTRACEMCO.NS",
    "NESTLEIND.NS",
    "POWERGRID.NS",
    "NTPC.NS",
    "BAJFINANCE.NS",
    "HCLTECH.NS",
    "WIPRO.NS",
    "TECHM.NS",
    "COALINDIA.NS",
]

INVESTING_INDIA_SLUGS = {
    "TCS": "tata-consultancy-services",
    "RELIANCE": "reliance-industries",
    "HDFCBANK": "hdfc-bank-ltd",
    "ICICIBANK": "icici-bank-ltd",
    "INFY": "infosys",
    "ITC": "itc",
    "BHARTIARTL": "bharti-airtel",
    "HINDUNILVR": "hindustan-unilever",
    "LT": "larsen---toubro",
    "SBIN": "state-bank-of-india",
    "KOTAKBANK": "kotak-mahindra-bank",
    "AXISBANK": "axis-bank",
    "MARUTI": "maruti-suzuki-india",
    "SUNPHARMA": "sun-pharma-advanced-research",
    "TITAN": "titan-industries",
    "ASIANPAINT": "asian-paints",
    "ULTRACEMCO": "ultratech-cement",
    "NESTLEIND": "nestle-india",
    "POWERGRID": "power-grid-corp.-of-india",
    "NTPC": "ntpc",
    "BAJFINANCE": "bajaj-finance",
    "HCLTECH": "hcl-technologies",
    "WIPRO": "wipro",
    "TECHM": "tech-mahindra",
    "COALINDIA": "coal-india",
}

LOW_RISK_SECTORS = {
    "Consumer Defensive",
    "Healthcare",
    "Technology",
    "Communication Services",
    "Financial Services",
    "Industrials",
    "Utilities",
}

INDUSTRY_OUTLOOKS = {
    "Technology": "Selective demand recovery; large-caps remain cash-rich, but discretionary global IT spend is still the key swing factor.",
    "Financial Services": "Credit demand remains structurally healthy; watch deposit costs, asset quality, and regulator-driven margin pressure.",
    "Consumer Defensive": "Premium staples and rural recovery are supportive; margin expansion depends on commodity inflation staying benign.",
    "Consumer Cyclical": "Urban discretionary demand is uneven; leaders with pricing power and distribution depth remain better placed.",
    "Healthcare": "Domestic formulations and specialty exports provide resilience; US pricing pressure and regulatory inspections remain risks.",
    "Industrials": "Capex, defense, power, and infrastructure ordering remain supportive, though valuations can become demanding.",
    "Basic Materials": "Cyclical earnings are tied to China demand, commodity prices, and operating leverage; prefer balance-sheet strength.",
    "Energy": "Cash flows are strong but policy, crude volatility, and refining margins can quickly change the risk-reward.",
    "Utilities": "Stable demand and regulated returns help downside protection; fuel costs and receivables need monitoring.",
    "Communication Services": "Tariff repair and data usage are positives; debt levels and competitive intensity remain important.",
    "Real Estate": "Premium residential absorption is healthy; rates, inventory discipline, and execution quality drive outcomes.",
    "Unavailable": "Sector details are unavailable; use extra caution and verify fundamentals before sizing the trade.",
}

DEFAULT_DAYS_TO_EXPIRY = 30
DEFAULT_RISK_FREE_RATE = 0.07
DEFAULT_IV = 0.16
DEFAULT_UPSIDE_THRESHOLD = 0.0
DATA_FETCH_TIMEOUT_SECONDS = 20
MAX_FETCH_WORKERS = 12


@dataclass(frozen=True)
class NewsItem:
    title: str
    link: str
    publisher: str
    related_symbol: str


@dataclass(frozen=True)
class StockSnapshot:
    symbol: str
    display_name: str
    sector: str | None
    industry: str | None
    summary: str | None
    cmp: float | None
    target_mean_price: float | None
    beta: float | None
    market_cap: float | None
    news: list[NewsItem]
    error: str | None = None


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def parse_nse_expiry(expiry_text: str) -> date:
    return pd.to_datetime(expiry_text, format="%d-%b-%Y").date()


@st.cache_data(ttl=6 * 60 * 60, show_spinner=False)
def fetch_stock_expiry_dates(stock_symbol: str = "RELIANCE") -> tuple[list[date], str | None]:
    try:
        response = requests.get(
            KITE_INSTRUMENTS_URL,
            timeout=25,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        instruments = pd.read_csv(StringIO(response.text), low_memory=False)
        stock_instruments = instruments[
            (instruments["exchange"] == "NFO")
            & (instruments["name"] == stock_symbol)
            & (instruments["expiry"].notna())
        ]
        expiry_dates = sorted(
            pd.to_datetime(stock_instruments["expiry"].dropna().unique()).date
        )
        if not expiry_dates:
            return [], f"Kite instrument dump returned no NFO expiries for {stock_symbol}."
        return expiry_dates, None
    except Exception as exc:
        return [], str(exc)


def next_stock_expiries_from_broker(
    stock_symbol: str = "RELIANCE",
    today: date | None = None,
    limit: int = 5,
) -> tuple[list[date], str | None]:
    current_date = today or date.today()
    expiry_dates, error = fetch_stock_expiry_dates(stock_symbol)
    if error:
        return [], error
    future_expiries = [expiry_date for expiry_date in expiry_dates if expiry_date > current_date]
    if not future_expiries:
        return [], f"No future stock expiries found for {stock_symbol}."
    return future_expiries[:limit], None


def days_until(expiry_date: date, today: date | None = None) -> int:
    current_date = today or date.today()
    return max(1, (expiry_date - current_date).days)


def put_delta_bsm(
    spot_price: float,
    strike_price: float,
    days_to_expiry: int = DEFAULT_DAYS_TO_EXPIRY,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    implied_volatility: float = DEFAULT_IV,
) -> float:
    if spot_price <= 0 or strike_price <= 0:
        raise ValueError("Spot and strike prices must be positive.")
    if days_to_expiry <= 0:
        raise ValueError("Days to expiry must be positive.")
    if implied_volatility <= 0:
        raise ValueError("Implied volatility must be positive.")

    time_to_expiry = days_to_expiry / 365.0
    d1 = (
        math.log(spot_price / strike_price)
        + (risk_free_rate + 0.5 * implied_volatility**2) * time_to_expiry
    ) / (implied_volatility * math.sqrt(time_to_expiry))
    return normal_cdf(d1) - 1.0


def strike_for_put_delta(
    spot_price: float,
    target_abs_delta: float,
    days_to_expiry: int,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    implied_volatility: float = DEFAULT_IV,
) -> float | None:
    if not 0 < target_abs_delta < 1 or spot_price <= 0:
        return None

    target_delta = -target_abs_delta
    lower = spot_price * 0.01
    upper = spot_price * 2.0

    try:
        lower_delta = put_delta_bsm(
            spot_price, lower, days_to_expiry, risk_free_rate, implied_volatility
        )
        upper_delta = put_delta_bsm(
            spot_price, upper, days_to_expiry, risk_free_rate, implied_volatility
        )
    except ValueError:
        return None

    if not lower_delta >= target_delta >= upper_delta:
        return None

    for _ in range(80):
        midpoint = (lower + upper) / 2.0
        midpoint_delta = put_delta_bsm(
            spot_price, midpoint, days_to_expiry, risk_free_rate, implied_volatility
        )
        if midpoint_delta > target_delta:
            lower = midpoint
        else:
            upper = midpoint

    return round((lower + upper) / 2.0, 2)


def first_float(*values: Any) -> float | None:
    for value in values:
        try:
            if value is None:
                continue
            numeric_value = float(value)
            if math.isfinite(numeric_value) and numeric_value > 0:
                return numeric_value
        except (TypeError, ValueError):
            continue
    return None


def clean_symbol(symbol: str) -> str:
    return symbol.replace(".NS", "").strip().upper()


def industry_outlook_for(sector: str | None) -> str:
    return INDUSTRY_OUTLOOKS.get(sector or "Unavailable", INDUSTRY_OUTLOOKS["Unavailable"])


def target_source_links(symbol: str) -> dict[str, str]:
    base_symbol = clean_symbol(symbol)
    company_query = quote_plus(f"{base_symbol} analyst forecast price target")
    tradingview_symbol = quote(f"NSE-{base_symbol}", safe="-")
    investing_slug = INVESTING_INDIA_SLUGS.get(base_symbol)
    investing_url = (
        f"https://in.investing.com/equities/{investing_slug}-consensus-estimates"
        if investing_slug
        else f"https://in.investing.com/search/?q={quote_plus(base_symbol)}"
    )
    return {
        "Yahoo Forecast": f"https://finance.yahoo.com/quote/{symbol}/analysis",
        "TradingView Forecast": f"https://www.tradingview.com/symbols/{tradingview_symbol}/forecast/",
        "MarketScreener": f"https://www.marketscreener.com/search/?q={quote_plus(base_symbol)}",
        "Investing Forecast": investing_url,
        "Refinitiv Note": f"https://www.google.com/search?q={company_query}+Refinitiv+consensus",
    }


def source_badges(symbol: str) -> str:
    links = target_source_links(symbol)
    return " ".join(
        f'<a class="target-pill" href="{escape(url, quote=True)}" target="_blank">{escape(name)}</a>'
        for name, url in links.items()
    )


def ipo_research_link(ipo_name: str) -> str:
    prompt = (
        f"{ipo_name} IPO research GMP financials valuation risks subscribe or avoid "
        "India IPO"
    )
    return f"https://www.perplexity.ai/search?q={quote_plus(prompt)}"


def gmp_research_note(gmp_text: str) -> str:
    cleaned = gmp_text.replace("₹", "").replace(",", "").strip()
    try:
        gmp_value = float(cleaned)
    except ValueError:
        return "Research"

    if gmp_value <= 0:
        return "Caution: flat GMP"
    if gmp_value < 10:
        return "Low premium: verify fundamentals"
    if gmp_value < 25:
        return "Moderate premium: research"
    return "High GMP: check valuation risk"


def first_number(text: str) -> float | None:
    numbers = re.findall(r"-?\d+(?:\.\d+)?", text)
    return float(numbers[0]) if numbers else None


def last_number(text: str) -> float | None:
    numbers = re.findall(r"-?\d+(?:\.\d+)?", text)
    return float(numbers[-1]) if numbers else None


def gmp_score(gmp_text: str, estimated_listing_text: str) -> float:
    if "%" in gmp_text:
        return last_number(gmp_text) or 0.0
    if "%" in estimated_listing_text:
        return last_number(estimated_listing_text) or 0.0
    return first_number(gmp_text) or 0.0


MONTH_NAMES = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def build_ipo_date(day: str, month_text: str, today: date | None = None) -> date | None:
    current_date = today or date.today()
    month = MONTH_NAMES.get(month_text.lower())
    if month is None:
        return None
    try:
        return date(current_date.year, month, int(day))
    except ValueError:
        return None


def format_ipo_date(value: date | None) -> str:
    return value.strftime("%d %b %Y") if value else "NA"


def parse_ipo_date_window(
    date_text: str, today: date | None = None
) -> tuple[str, str, date | None]:
    cleaned_text = (
        str(date_text)
        .replace(",", " ")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )

    same_month = re.search(
        r"\b(\d{1,2})\s*-\s*(\d{1,2})\s+([A-Za-z]+)\b", cleaned_text
    )
    if same_month:
        start_date = build_ipo_date(same_month.group(1), same_month.group(3), today)
        end_date = build_ipo_date(same_month.group(2), same_month.group(3), today)
        return format_ipo_date(start_date), format_ipo_date(end_date), end_date

    two_months = re.search(
        r"\b(\d{1,2})\s+([A-Za-z]+)\s*-\s*(\d{1,2})\s+([A-Za-z]+)\b",
        cleaned_text,
    )
    if two_months:
        start_date = build_ipo_date(two_months.group(1), two_months.group(2), today)
        end_date = build_ipo_date(two_months.group(3), two_months.group(4), today)
        return format_ipo_date(start_date), format_ipo_date(end_date), end_date

    single_date = re.search(r"\b(\d{1,2})\s+([A-Za-z]+)\b", cleaned_text)
    if single_date:
        start_date = build_ipo_date(single_date.group(1), single_date.group(2), today)
        return format_ipo_date(start_date), "NA", None

    return "NA", "NA", None


def parse_ipo_end_date(date_text: str, today: date | None = None) -> date | None:
    _, _, end_date = parse_ipo_date_window(date_text, today)
    return end_date


def enrich_ipo_frame(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    date_windows = frame["Date"].map(parse_ipo_date_window)
    frame["IPO Start Date"] = date_windows.map(lambda value: value[0])
    frame["IPO Last Date"] = date_windows.map(lambda value: value[1])
    frame["Research Note"] = frame["IPO GMP"].map(gmp_research_note)
    frame["Alert"] = frame.apply(ipo_alert_text, axis=1)
    frame["AI Research"] = frame["IPO Name"].map(ipo_research_link)
    return frame


def ipo_alert_text(row: pd.Series, today: date | None = None) -> str:
    end_date = parse_ipo_end_date(str(row.get("Date", "")), today)
    if end_date is None:
        return ""
    current_date = today or date.today()
    second_last_day = end_date - timedelta(days=1)
    score = gmp_score(str(row.get("IPO GMP", "")), str(row.get("Est. Listing", "")))
    if current_date == second_last_day and score >= 10:
        return f"Alert: good GMP on 2nd last day ({score:.1f}%)"
    return ""


def fallback_open_ipos() -> pd.DataFrame:
    rows = [
        {
            "IPO Name": "Jivial Industries",
            "IPO GMP": "₹0",
            "Price Band": "₹196",
            "Est. Listing": "₹- (0.00%)",
            "Date": "23-25 June",
            "Type": "BSE SME",
            "Status": "Open",
            "Last Updated": "Fallback",
            "Source": "https://ipowatch.in/jivial-industries-ipo/",
        },
        {
            "IPO Name": "Shreedhar Spinners",
            "IPO GMP": "₹0",
            "Price Band": "₹53",
            "Est. Listing": "₹- (0.00%)",
            "Date": "23-25 June",
            "Type": "NSE SME",
            "Status": "Open",
            "Last Updated": "Fallback",
            "Source": "https://ipowatch.in/shreedhar-spinners-ipo/",
        },
        {
            "IPO Name": "Advit Jewels",
            "IPO GMP": "Around 40%",
            "Price Band": "NA",
            "Est. Listing": "Positive GMP",
            "Date": "Opened 23 June",
            "Type": "SME",
            "Status": "Open",
            "Last Updated": "Fallback",
            "Source": "https://m.economictimes.com/markets/ipos/fpos/advit-jewels-ipo-opens-today-check-brokerages-review-gmp-subscription-and-other-details/articleshow/131923074.cms",
        },
        {
            "IPO Name": "Waterways Leisure Tourism",
            "IPO GMP": "Around 2%",
            "Price Band": "NA",
            "Est. Listing": "Muted GMP",
            "Date": "23-25 June",
            "Type": "SME",
            "Status": "Open",
            "Last Updated": "Fallback",
            "Source": "https://m.economictimes.com/markets/ipos/fpos/waterways-leisure-tourism-ipo-opens-for-subscription-today-should-you-subscribe/articleshow/131923161.cms",
        },
    ]
    frame = pd.DataFrame(rows)
    return enrich_ipo_frame(frame)


@st.cache_data(ttl=30 * 60, show_spinner=False)
def fetch_open_ipos() -> tuple[pd.DataFrame, str]:
    try:
        response = requests.get(
            IPOWATCH_GMP_URL,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")
        if not tables:
            raise ValueError("No IPO GMP table found.")

        ipo_rows = []
        for table in tables:
            header_cells = [
                cell.get_text(" ", strip=True)
                for cell in table.find("tr").find_all(["th", "td"])
            ]
            if "IPO Name" not in header_cells or "IPO GMP" not in header_cells:
                continue

            for row in table.find_all("tr")[1:]:
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
                if len(cells) < len(header_cells):
                    continue
                record = dict(zip(header_cells, cells))
                if record.get("Status", "").lower() != "open":
                    continue
                link = row.find("a")
                record["Source"] = link.get("href") if link else IPOWATCH_GMP_URL
                ipo_rows.append(record)
            break

        if not ipo_rows:
            raise ValueError("No open IPO rows found in IPOWatch GMP table.")

        frame = pd.DataFrame(ipo_rows)
        for column in [
            "IPO Name",
            "IPO GMP",
            "Price Band",
            "Est. Listing",
            "Date",
            "Type",
            "Status",
            "Last Updated",
            "Source",
        ]:
            if column not in frame.columns:
                frame[column] = "NA"

        frame = frame[
            [
                "IPO Name",
                "IPO GMP",
                "Price Band",
                "Est. Listing",
                "Date",
                "Type",
                "Status",
                "Last Updated",
                "Source",
            ]
        ]
        return enrich_ipo_frame(frame), "IPOWatch"
    except Exception:
        return fallback_open_ipos(), "Fallback"


def extract_news_item(item: dict[str, Any], symbol: str) -> NewsItem | None:
    content = item.get("content", {})
    title = item.get("title") or content.get("title")
    link = item.get("link") or content.get("canonicalUrl", {}).get("url")
    publisher = item.get("publisher") or content.get("provider", {}).get("displayName")

    if not title:
        return None

    return NewsItem(
        title=str(title),
        link=str(link) if link else "",
        publisher=str(publisher) if publisher else "Market news",
        related_symbol=symbol,
    )


def current_price_from_history(ticker: yf.Ticker) -> float | None:
    history = ticker.history(period="5d", interval="1d", auto_adjust=False)
    if history.empty or "Close" not in history.columns:
        return None
    return first_float(history["Close"].dropna().iloc[-1])


def empty_snapshot(symbol: str, error: str) -> StockSnapshot:
    return StockSnapshot(
        symbol=symbol,
        display_name=clean_symbol(symbol),
        sector=None,
        industry=None,
        summary=None,
        cmp=None,
        target_mean_price=None,
        beta=None,
        market_cap=None,
        news=[],
        error=error,
    )


def fetch_stock_snapshot(symbol: str, include_news: bool = False) -> StockSnapshot:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.get_info()

        fast_info = getattr(ticker, "fast_info", {})
        fast_last_price = None
        try:
            fast_last_price = fast_info.get("last_price")
        except AttributeError:
            fast_last_price = None

        cmp = first_float(
            fast_last_price,
            info.get("currentPrice"),
            info.get("regularMarketPrice"),
            info.get("previousClose"),
            current_price_from_history(ticker),
        )
        target = first_float(info.get("targetMeanPrice"))
        display_name = info.get("shortName") or info.get("longName") or clean_symbol(symbol)

        raw_news = []
        if include_news:
            try:
                raw_news = ticker.news or []
            except Exception:
                raw_news = []

        news = [
            parsed
            for parsed in (extract_news_item(item, symbol) for item in raw_news[:10])
            if parsed is not None
        ]

        return StockSnapshot(
            symbol=symbol,
            display_name=str(display_name),
            sector=info.get("sector"),
            industry=info.get("industry"),
            summary=info.get("longBusinessSummary") or info.get("shortBusinessSummary"),
            cmp=cmp,
            target_mean_price=target,
            beta=first_float(info.get("beta")),
            market_cap=first_float(info.get("marketCap")),
            news=news,
        )
    except Exception as exc:
        return empty_snapshot(symbol, str(exc))


@st.cache_data(ttl=15 * 60, show_spinner="Fetching F&O stock data...")
def fetch_universe_snapshots(symbols: tuple[str, ...]) -> list[StockSnapshot]:
    snapshots_by_symbol: dict[str, StockSnapshot] = {}
    executor = ThreadPoolExecutor(max_workers=MAX_FETCH_WORKERS)
    future_to_symbol = {
        executor.submit(fetch_stock_snapshot, symbol): symbol for symbol in symbols
    }

    done, not_done = wait(future_to_symbol, timeout=DATA_FETCH_TIMEOUT_SECONDS)
    for future in done:
        symbol = future_to_symbol[future]
        try:
            snapshots_by_symbol[symbol] = future.result()
        except Exception as exc:
            snapshots_by_symbol[symbol] = empty_snapshot(symbol, str(exc))

    for future in not_done:
        symbol = future_to_symbol[future]
        future.cancel()
        snapshots_by_symbol[symbol] = empty_snapshot(
            symbol,
            f"Timed out after {DATA_FETCH_TIMEOUT_SECONDS} seconds",
        )

    executor.shutdown(wait=False, cancel_futures=True)
    return [snapshots_by_symbol[symbol] for symbol in symbols]


def build_shortlist(
    snapshots: list[StockSnapshot],
    upside_threshold: float,
    days_to_expiry: int,
    low_risk_only: bool,
    apply_upside_filter: bool,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    implied_volatility: float = DEFAULT_IV,
) -> pd.DataFrame:
    rows = []
    for snapshot in snapshots:
        if snapshot.cmp is None:
            continue
        if low_risk_only and snapshot.sector not in LOW_RISK_SECTORS:
            continue

        upside = (
            ((snapshot.target_mean_price - snapshot.cmp) / snapshot.cmp) * 100.0
            if snapshot.target_mean_price is not None
            else None
        )
        if apply_upside_filter and (upside is None or upside < upside_threshold):
            continue

        rows.append(
            {
                "Stock": snapshot.symbol,
                "Company": snapshot.display_name,
                "Sector": snapshot.sector or "Unavailable",
                "Industry": snapshot.industry or "Unavailable",
                "CMP": snapshot.cmp,
                "Consensus Target": snapshot.target_mean_price,
                "Upside %": upside,
                "Beta": snapshot.beta,
                "Industry Outlook": industry_outlook_for(snapshot.sector),
                "0.15 Delta Put Strike": strike_for_put_delta(
                    snapshot.cmp,
                    0.15,
                    days_to_expiry,
                    risk_free_rate,
                    implied_volatility,
                ),
                "0.30 Delta Put Strike": strike_for_put_delta(
                    snapshot.cmp,
                    0.30,
                    days_to_expiry,
                    risk_free_rate,
                    implied_volatility,
                ),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "Stock",
                "Company",
                "Sector",
                "Industry",
                "CMP",
                "Consensus Target",
                "Upside %",
                "Beta",
                "Industry Outlook",
                "0.15 Delta Put Strike",
                "0.30 Delta Put Strike",
            ]
        )
    return pd.DataFrame(rows).sort_values("Upside %", ascending=False, ignore_index=True)


def format_inr(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"Rs. {value:,.2f}"


def format_large_inr(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "NA"
    crore = value / 10_000_000
    return f"Rs. {crore:,.0f} Cr"


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; }
        .metric-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .75rem;
            margin: .75rem 0 1.1rem;
        }
        .metric-card, .news-card, .profile-panel, .mobile-card {
            border: 1px solid #d9dee8;
            background: #ffffff;
            border-radius: 8px;
            padding: .9rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, .05);
        }
        .metric-label {
            color: #5f6b7a;
            font-size: .78rem;
            margin-bottom: .25rem;
        }
        .metric-value {
            color: #111827;
            font-size: 1.05rem;
            font-weight: 700;
        }
        .target-pill {
            display: inline-block;
            margin: 0 .25rem .25rem 0;
            padding: .18rem .45rem;
            border: 1px solid #c8d3e3;
            border-radius: 999px;
            color: #174ea6 !important;
            background: #f7faff;
            text-decoration: none !important;
            font-size: .78rem;
            white-space: nowrap;
        }
        .news-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .75rem;
        }
        .news-card a {
            color: #111827;
            font-weight: 700;
            text-decoration: none;
        }
        .news-meta {
            color: #667085;
            font-size: .8rem;
            margin-top: .35rem;
        }
        .profile-panel {
            margin-bottom: 1rem;
            line-height: 1.45;
        }
        .mobile-card {
            margin-bottom: .75rem;
        }
        .mobile-card-title {
            font-weight: 800;
            color: #111827;
            margin-bottom: .15rem;
        }
        .mobile-card-subtitle {
            color: #667085;
            font-size: .82rem;
            margin-bottom: .7rem;
        }
        .mobile-card-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .55rem;
            margin-bottom: .65rem;
        }
        .mobile-card-label {
            color: #667085;
            font-size: .72rem;
            line-height: 1.2;
        }
        .mobile-card-value {
            color: #111827;
            font-weight: 700;
            font-size: .9rem;
            line-height: 1.25;
        }
        .mobile-card-note {
            color: #374151;
            font-size: .8rem;
            line-height: 1.35;
        }
        @media (max-width: 900px) {
            .metric-strip, .news-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_strip(snapshot: StockSnapshot) -> None:
    cards = [
        ("CMP", format_inr(snapshot.cmp)),
        ("Consensus Target", format_inr(snapshot.target_mean_price)),
        ("Beta", "NA" if snapshot.beta is None else f"{snapshot.beta:.2f}"),
        ("Market Cap", format_large_inr(snapshot.market_cap)),
    ]
    html = '<div class="metric-strip">'
    for label, value in cards:
        html += (
            '<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            "</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_value(label: str, value: str) -> str:
    return (
        "<div>"
        f'<div class="mobile-card-label">{escape(label)}</div>'
        f'<div class="mobile-card-value">{escape(value)}</div>'
        "</div>"
    )


def render_stock_cards(display_df: pd.DataFrame) -> None:
    for _, row in display_df.iterrows():
        upside = row["Upside %"]
        upside_text = "NA" if pd.isna(upside) else f"{upside:.2f}%"
        beta = row["Beta"]
        beta_text = "NA" if pd.isna(beta) else f"{beta:.2f}"
        html = (
            '<div class="mobile-card">'
            f'<div class="mobile-card-title">{escape(str(row["Stock"]))}</div>'
            f'<div class="mobile-card-subtitle">{escape(str(row["Company"]))}</div>'
            '<div class="mobile-card-grid">'
            + render_value("CMP", format_inr(row["CMP"]))
            + render_value("Target", format_inr(row["Consensus Target"]))
            + render_value("Upside", upside_text)
            + render_value("Beta", beta_text)
            + render_value("0.15 Delta", format_inr(row["0.15 Delta Put Strike"]))
            + render_value("0.30 Delta", format_inr(row["0.30 Delta Put Strike"]))
            + "</div>"
            f'<div class="mobile-card-note"><strong>{escape(str(row["Sector"]))}</strong> | '
            f'{escape(str(row["Industry"]))}<br>{escape(str(row["Industry Outlook"]))}</div>'
            "</div>"
        )
        st.markdown(html, unsafe_allow_html=True)
        with st.expander("Forecast links"):
            st.markdown(source_badges(str(row["Stock"])), unsafe_allow_html=True)


def render_shortlist_tab(shortlist: pd.DataFrame, corpus: float) -> None:
    if shortlist.empty:
        st.info("No F&O stocks currently meet the selected filters.")
        return

    display_df = shortlist.copy()
    display_columns = [
        "Stock",
        "Company",
        "Sector",
        "CMP",
        "Consensus Target",
        "Upside %",
        "Beta",
        "0.15 Delta Put Strike",
        "0.30 Delta Put Strike",
        "Industry",
        "Industry Outlook",
    ]

    view_mode = st.radio(
        "View mode",
        ["Cards", "Table"],
        horizontal=True,
        help="Use Cards on phone; Table is better on desktop.",
    )

    if view_mode == "Cards":
        sort_col, search_col = st.columns([1.2, 2.5])
        with sort_col:
            sort_by = st.selectbox(
                "Sort cards by",
                ["Upside %", "CMP", "Beta", "Stock"],
            )
        with search_col:
            query = st.text_input("Search stock/company", "")
        card_df = display_df.copy()
        if query.strip():
            needle = query.strip().lower()
            card_df = card_df[
                card_df["Stock"].str.lower().str.contains(needle, na=False)
                | card_df["Company"].str.lower().str.contains(needle, na=False)
            ]
        ascending = sort_by in {"Stock"}
        card_df = card_df.sort_values(sort_by, ascending=ascending, na_position="last")
        render_stock_cards(card_df)
    else:
        controls_col, links_col = st.columns([1.4, 4.6])
        with controls_col:
            forecast_symbol = st.selectbox(
                "Links for",
                shortlist["Stock"].tolist(),
                format_func=lambda symbol: (
                    f"{symbol} - "
                    f"{shortlist.loc[shortlist['Stock'] == symbol, 'Company'].iloc[0]}"
                ),
                label_visibility="collapsed",
                help="Choose a stock to see every forecast source.",
            )
        with links_col:
            st.markdown(source_badges(forecast_symbol), unsafe_allow_html=True)

        table_height = min(7200, max(260, 36 * (len(display_df) + 1)))
        st.dataframe(
            display_df[display_columns],
            use_container_width=True,
            hide_index=True,
            height=table_height,
            column_config={
                "CMP": st.column_config.NumberColumn("CMP", format="Rs. %.2f"),
                "Consensus Target": st.column_config.NumberColumn(
                    "Consensus Target", format="Rs. %.2f"
                ),
                "Upside %": st.column_config.NumberColumn("Upside %", format="%.2f%%"),
                "Beta": st.column_config.NumberColumn("Beta", format="%.2f"),
                "0.15 Delta Put Strike": st.column_config.NumberColumn(
                    "0.15 Delta Put Strike", format="Rs. %.2f"
                ),
                "0.30 Delta Put Strike": st.column_config.NumberColumn(
                    "0.30 Delta Put Strike", format="Rs. %.2f"
                ),
            },
        )
    st.caption(
        "Use Cards on phone and Table on desktop. Forecast links are inside each card "
        "or above the desktop table. "
        "Investing uses direct India consensus-estimates pages where available. "
        "Refinitiv/LSEG consensus generally requires a licensed feed."
    )

    lowest_standard_strike = shortlist["0.30 Delta Put Strike"].dropna().min()
    if lowest_standard_strike:
        approx_positions = math.floor(corpus / lowest_standard_strike)
        st.caption(
            "Corpus check: "
            f"{format_inr(corpus)} can secure roughly {approx_positions:,} shares "
            "at the lowest displayed 0.30-delta strike, before exchange lot-size rules."
        )


def render_news_cards(snapshot: StockSnapshot) -> None:
    if not snapshot.news:
        st.info("No recent headlines were returned by the data provider.")
        return

    html = '<div class="news-grid">'
    for item in snapshot.news:
        title = escape(item.title)
        href = item.link or target_source_links(snapshot.symbol)["Yahoo Forecast"]
        html += (
            '<div class="news-card">'
            f'<a href="{escape(href, quote=True)}" target="_blank">{title}</a>'
            f'<div class="news-meta">{escape(item.publisher)} | {escape(clean_symbol(item.related_symbol))}</div>'
            "</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_target_sources(snapshot: StockSnapshot) -> None:
    st.markdown("##### Target Cross-Checks")
    st.markdown(source_badges(snapshot.symbol), unsafe_allow_html=True)
    st.caption(
        "Yahoo provides the numeric consensus used in the table. TradingView and "
        "Investing India provide public forecast/consensus pages for many NSE symbols. "
        "Refinitiv/LSEG consensus generally requires a licensed terminal/feed."
    )


def render_stock_detail(snapshot: StockSnapshot) -> None:
    st.subheader(f"{snapshot.display_name} ({snapshot.symbol})")
    render_metric_strip(snapshot)

    col_profile, col_outlook = st.columns([1.4, 1])
    with col_profile:
        st.markdown(
            f"""
            <div class="profile-panel">
                <strong>Sector:</strong> {escape(snapshot.sector or "Unavailable")}<br>
                <strong>Industry:</strong> {escape(snapshot.industry or "Unavailable")}<br><br>
                {escape(snapshot.summary or "Company summary is unavailable from the data provider.")}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_outlook:
        st.markdown(
            f"""
            <div class="profile-panel">
                <strong>Industry Outlook</strong><br><br>
                {escape(industry_outlook_for(snapshot.sector))}
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_target_sources(snapshot)

    st.subheader("Stock-Specific News")
    render_news_cards(snapshot)


def render_deep_dive_tab(available_symbols: list[str]) -> None:
    if "deep_dive_symbols" not in st.session_state:
        st.session_state.deep_dive_symbols = []

    st.caption(
        "Search and add any stock from the full F&O universe. Checked selections are "
        "remembered while this app session is open."
    )
    selected_symbols = st.multiselect(
        "Select stocks for news",
        options=available_symbols,
        key="deep_dive_symbols",
        help="News is fetched only for selected stocks.",
    )

    if not selected_symbols:
        st.info("Select at least one stock to load its detail and news.")
        return

    st.markdown("##### Selected")
    kept_symbols: list[str] = []
    checkbox_columns = st.columns(4)
    for index, symbol in enumerate(selected_symbols):
        with checkbox_columns[index % 4]:
            if st.checkbox(symbol, value=True, key=f"deep_dive_keep_{symbol}"):
                kept_symbols.append(symbol)
    if kept_symbols != selected_symbols:
        st.session_state.deep_dive_symbols = kept_symbols
        st.rerun()

    for selected_symbol in kept_symbols:
        with st.spinner(f"Loading news for {selected_symbol}..."):
            snapshot = fetch_stock_snapshot(selected_symbol, include_news=True)
        render_stock_detail(snapshot)
        st.divider()


def render_ipo_cards(ipo_frame: pd.DataFrame) -> None:
    for _, row in ipo_frame.iterrows():
        html = (
            '<div class="mobile-card">'
            f'<div class="mobile-card-title">{escape(str(row["IPO Name"]))}</div>'
            f'<div class="mobile-card-subtitle">{escape(str(row["Type"]))} | '
            f'{escape(str(row["IPO Start Date"]))} to '
            f'{escape(str(row["IPO Last Date"]))}</div>'
            '<div class="mobile-card-grid">'
            + render_value("GMP", str(row["IPO GMP"]))
            + render_value("Price Band", str(row["Price Band"]))
            + render_value("Est. Listing", str(row["Est. Listing"]))
            + render_value("IPO Start", str(row["IPO Start Date"]))
            + render_value("Last Date", str(row["IPO Last Date"]))
            + render_value("Status", str(row["Status"]))
            + "</div>"
            f'<div class="mobile-card-note">{escape(str(row["Research Note"]))}'
            f'{("<br>" + escape(str(row["Alert"]))) if str(row["Alert"]) else ""}</div>'
            "</div>"
        )
        st.markdown(html, unsafe_allow_html=True)
        link_cols = st.columns(2)
        with link_cols[0]:
            st.link_button("IPO Details", str(row["Source"]), use_container_width=True)
        with link_cols[1]:
            st.link_button("AI Research", str(row["AI Research"]), use_container_width=True)


def render_ipo_tab() -> None:
    ipo_frame, source_name = fetch_open_ipos()
    st.caption(
        f"Source: {source_name}. GMP is unofficial grey-market data and can change quickly."
    )
    if ipo_frame.empty:
        st.info("No open IPOs found from the current source.")
        return

    active_alerts = ipo_frame[ipo_frame["Alert"].astype(str).str.len() > 0]
    if not active_alerts.empty:
        for _, row in active_alerts.iterrows():
            st.warning(f"{row['IPO Name']}: {row['Alert']}")

    view_mode = st.radio("IPO view", ["Cards", "Table"], horizontal=True)
    if view_mode == "Cards":
        render_ipo_cards(ipo_frame)
        st.caption(
            "Research note is a simple GMP-based flag, not a recommendation. Review "
            "financials, valuation, promoter background, and listing risk before deciding."
        )
        return

    display_columns = [
        "IPO Name",
        "IPO GMP",
        "Price Band",
        "Est. Listing",
        "Date",
        "IPO Start Date",
        "IPO Last Date",
        "Type",
        "Status",
        "Alert",
        "Research Note",
        "Last Updated",
        "Source",
        "AI Research",
    ]
    st.dataframe(
        ipo_frame[display_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Source": st.column_config.LinkColumn(
                "IPO Source", display_text="Details"
            ),
            "AI Research": st.column_config.LinkColumn(
                "AI Research", display_text="Research"
            ),
        },
    )
    st.caption(
        "Research note is a simple GMP-based flag, not a recommendation. Use the AI "
        "research link to review financials, valuation, promoter background, objects "
        "of issue, and listing risk before deciding."
    )


def render_data_quality_warnings(snapshots: list[StockSnapshot]) -> None:
    failed_symbols = [snapshot.symbol for snapshot in snapshots if snapshot.error]
    missing_targets = [
        snapshot.symbol
        for snapshot in snapshots
        if not snapshot.error and snapshot.target_mean_price is None
    ]

    if snapshots and len(failed_symbols) == len(snapshots):
        first_error = next((snapshot.error for snapshot in snapshots if snapshot.error), "")
        st.error(
            "Market data could not be reached for this scan. "
            "If your internet is working, wait a minute and use Refresh Data. "
            f"Provider message: {first_error}"
        )
        return

    if failed_symbols:
        st.warning(f"Could not fetch data for: {', '.join(failed_symbols[:20])}")
    if missing_targets:
        st.warning(
            "Analyst target price was unavailable for: "
            + ", ".join(missing_targets[:20])
            + ("..." if len(missing_targets) > 20 else "")
        )


def main() -> None:
    st.set_page_config(
        page_title="Cash-Secured Put Tracker",
        page_icon="Rs",
        layout="wide",
    )
    inject_css()

    st.title("Cash-Secured Put Strategy Tracker")
    st.caption(
        "F&O-wide Indian equity screen for conservative cash-secured put ideas. "
        "Targets and news are sourced from Yahoo Finance via yfinance, with linked "
        "research cross-checks."
    )

    fo_symbols = FO_SYMBOLS
    universe_source = "Hardcoded F&O universe"
    today = date.today()

    with st.sidebar:
        st.header("Strategy Inputs")
        corpus = st.number_input(
            "Total Corpus",
            min_value=100_000,
            value=5_000_000,
            step=100_000,
            format="%d",
        )
        apply_upside_filter = st.toggle("Apply upside filter", value=False)
        upside_threshold = st.slider(
            "Target Upside Threshold",
            min_value=0.0,
            max_value=40.0,
            value=DEFAULT_UPSIDE_THRESHOLD,
            step=0.5,
            disabled=not apply_upside_filter,
        )
        implied_volatility = st.number_input(
            "Default IV",
            min_value=0.01,
            max_value=1.00,
            value=DEFAULT_IV,
            step=0.01,
            format="%.2f",
        )
        low_risk_only = st.toggle("Prefer defensive / low-risk sectors", value=False)
        selected_scan_symbols = st.multiselect(
            "F&O stocks to scan",
            options=fo_symbols,
            default=fo_symbols,
            help="All hardcoded F&O stocks load by default. Remove names if you want a faster scan.",
        )
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.caption(
            f"{universe_source}: {len(fo_symbols)} stocks. "
            f"Selected scan is capped at {DATA_FETCH_TIMEOUT_SECONDS}s. "
            "Risk-free rate is 7.0%."
        )

    selected_universe = tuple(selected_scan_symbols)
    if not selected_universe:
        st.warning("Select at least one F&O stock from the sidebar to run the scan.")
        return

    expiry_dates, expiry_error = next_stock_expiries_from_broker("RELIANCE", today, limit=3)
    selected_expiry = None
    if expiry_dates:
        selected_expiry = expiry_dates[0]
    days_to_expiry = (
        days_until(selected_expiry, today)
        if selected_expiry is not None
        else DEFAULT_DAYS_TO_EXPIRY
    )

    expiry_col, days_col, status_col = st.columns([1.5, 1, 4.5])
    with expiry_col:
        if expiry_dates:
            selected_expiry = st.selectbox(
                "Expiry",
                options=expiry_dates,
                format_func=lambda value: value.strftime("%d %b %Y"),
            )
            days_to_expiry = days_until(selected_expiry, today)
        else:
            st.selectbox("Expiry", ["Unavailable"], disabled=True)
    with days_col:
        st.metric(
            "Days",
            f"{days_to_expiry}",
            "fallback" if selected_expiry is None else None,
        )
    with status_col:
        if expiry_error:
            st.warning(f"Expiry fetch failed: {expiry_error}")

    snapshots = fetch_universe_snapshots(selected_universe)
    successful_fetches = sum(1 for snapshot in snapshots if snapshot.error is None)
    st.caption(f"Loaded {successful_fetches} of {len(selected_universe)} selected F&O stocks.")
    shortlist = build_shortlist(
        snapshots=snapshots,
        upside_threshold=upside_threshold,
        days_to_expiry=days_to_expiry,
        low_risk_only=low_risk_only,
        apply_upside_filter=apply_upside_filter,
        implied_volatility=implied_volatility,
    )

    render_data_quality_warnings(snapshots)

    tab_ideas, tab_deep_dive, tab_ipos = st.tabs(
        ["All Ideas", "Deep Dive & News", "Open IPOs"]
    )
    with tab_ideas:
        render_shortlist_tab(shortlist, float(corpus))
    with tab_deep_dive:
        render_deep_dive_tab(fo_symbols)
    with tab_ipos:
        render_ipo_tab()

    st.caption(
        "Educational tool only. Verify option chains, lot sizes, liquidity, margin, "
        "tax impact, and broker prices before placing trades."
    )


if __name__ == "__main__":
    main()
