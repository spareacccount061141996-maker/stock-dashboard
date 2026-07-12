from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup


IPOWATCH_GMP_URL = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"
STATE_FILE = Path(".notification-state/ipo_alerts.json")


@dataclass(frozen=True)
class IpoAlert:
    name: str
    ipo_type: str
    gmp: str
    estimated_listing: str
    subscription_date: str
    gmp_percent: float
    threshold_percent: float
    source: str

    @property
    def key(self) -> str:
        today_key = date.today().isoformat()
        return f"{today_key}|{self.name.lower()}|{self.threshold_percent:.0f}"


def parse_percent(text: str) -> float | None:
    matches = re.findall(r"(-?\d+(?:\.\d+)?)\s*%", str(text))
    if not matches:
        return None
    return float(matches[-1])


def alert_threshold(ipo_type: str) -> tuple[str, float]:
    if "sme" in ipo_type.lower():
        return "SME", 25.0
    return "Mainboard", 10.0


def fetch_open_ipo_rows() -> list[dict[str, str]]:
    response = requests.get(
        IPOWATCH_GMP_URL,
        timeout=25,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for table in soup.find_all("table"):
        header_row = table.find("tr")
        if header_row is None:
            continue
        headers = [
            cell.get_text(" ", strip=True)
            for cell in header_row.find_all(["th", "td"])
        ]
        if "IPO Name" not in headers or "IPO GMP" not in headers:
            continue

        rows: list[dict[str, str]] = []
        for row in table.find_all("tr")[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
            if len(cells) < len(headers):
                continue
            record = dict(zip(headers, cells))
            if record.get("Status", "").lower() != "open":
                continue
            link = row.find("a")
            record["Source"] = link.get("href") if link else IPOWATCH_GMP_URL
            rows.append(record)
        return rows
    return []


def build_alerts(rows: Iterable[dict[str, str]]) -> list[IpoAlert]:
    alerts: list[IpoAlert] = []
    for row in rows:
        ipo_type = row.get("Type", "")
        board_label, threshold = alert_threshold(ipo_type)
        gmp_percent = parse_percent(row.get("Est. Listing", ""))
        if gmp_percent is None:
            gmp_percent = parse_percent(row.get("IPO GMP", ""))
        if gmp_percent is None or gmp_percent < threshold:
            continue

        alerts.append(
            IpoAlert(
                name=row.get("IPO Name", "Unknown IPO"),
                ipo_type=board_label,
                gmp=row.get("IPO GMP", "NA"),
                estimated_listing=row.get("Est. Listing", "NA"),
                subscription_date=row.get("Date", "NA"),
                gmp_percent=gmp_percent,
                threshold_percent=threshold,
                source=row.get("Source", IPOWATCH_GMP_URL),
            )
        )
    return alerts


def load_sent_keys() -> set[str]:
    if not STATE_FILE.exists():
        return set()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    return set(data.get("sent_keys", []))


def save_sent_keys(sent_keys: set[str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {"sent_keys": sorted(sent_keys)}
    STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def telegram_message(alerts: list[IpoAlert]) -> str:
    lines = ["IPO GMP alert"]
    for alert in alerts:
        lines.extend(
            [
                "",
                f"{alert.name}",
                f"Type: {alert.ipo_type}",
                f"GMP signal: {alert.gmp_percent:.1f}% "
                f"(threshold {alert.threshold_percent:.0f}%)",
                f"GMP: {alert.gmp}",
                f"Est. listing: {alert.estimated_listing}",
                f"Subscribe: {alert.subscription_date}",
                f"Details: {alert.source}",
            ]
        )
    return "\n".join(lines)


def send_telegram(message: str, bot_token: str, chat_id: str) -> None:
    response = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        timeout=20,
        json={
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": True,
        },
    )
    response.raise_for_status()


def main() -> int:
    parser = argparse.ArgumentParser(description="Send IPO GMP mobile alerts.")
    parser.add_argument("--dry-run", action="store_true", help="Print alerts without sending.")
    parser.add_argument(
        "--test-message",
        action="store_true",
        help="Send a Telegram test notification and skip IPO scanning.",
    )
    args = parser.parse_args()

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if args.test_message:
        message = (
            "IPO alert test\n\n"
            "Telegram mobile notifications are connected correctly."
        )
        if args.dry_run:
            print(message)
            return 0
        if not bot_token or not chat_id:
            print("Telegram secrets are missing; test notification was not sent.")
            return 0
        send_telegram(message, bot_token, chat_id)
        print("Sent Telegram test notification.")
        return 0

    rows = fetch_open_ipo_rows()
    alerts = build_alerts(rows)
    sent_keys = load_sent_keys()
    unsent_alerts = [alert for alert in alerts if alert.key not in sent_keys]

    if not unsent_alerts:
        print("No new IPO alerts matched the mobile notification rules.")
        return 0

    message = telegram_message(unsent_alerts)
    if args.dry_run:
        print(message)
    else:
        if not bot_token or not chat_id:
            print("Telegram secrets are missing; alerts were detected but not sent.")
            print(message)
            return 0
        send_telegram(message, bot_token, chat_id)
        print(f"Sent {len(unsent_alerts)} IPO mobile alert(s).")

    sent_keys.update(alert.key for alert in unsent_alerts)
    save_sent_keys(sent_keys)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
