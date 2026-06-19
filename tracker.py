"""
Realty Income → Xtrackers MSCI World Tausch-Tracker
Optimierungsziel: maximale ETF-Anteile aus 60 O-Aktien

Konfiguration via GitHub Secrets:
  TELEGRAM_TOKEN   – Bot-Token von @BotFather
  TELEGRAM_CHAT_ID – deine Chat-ID (von @userinfobot)
"""

import yfinance as yf
import requests
import json
import os
import sys
from datetime import datetime, timezone

# ── Konfiguration ──────────────────────────────────────────────────────────────
SHARES_SELL = 60
SELL_TICKER = "O"        # Realty Income – NYSE (USD)
BUY_TICKER  = "UDIV.DE"  # Global X SuperDividend UCITS ETF – Xetra
FX_TICKER   = "EURUSD=X" # Wechselkurs

BEST_FILE   = "best.json"
HISTORY_FILE = "history.json"

TG_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# UTC-Stunde des ersten Tages-Runs (8 UTC = 9 Uhr MEZ / 10 Uhr MESZ)
MORNING_HOUR_UTC = 8


# ── Kurse abrufen ──────────────────────────────────────────────────────────────
def get_prices() -> dict:
    """Aktuelle Kurse und berechnete ETF-Anteile abrufen."""
    try:
        sell_info = yf.Ticker(SELL_TICKER).fast_info
        buy_info  = yf.Ticker(BUY_TICKER).fast_info
        fx_info   = yf.Ticker(FX_TICKER).fast_info

        sell_usd  = sell_info.last_price
        buy_eur   = buy_info.last_price
        eurusd    = fx_info.last_price

        sell_eur   = sell_usd / eurusd
        total_eur  = sell_eur * SHARES_SELL
        etf_shares = total_eur / buy_eur

        return {
            "timestamp"      : datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "O_usd"          : round(sell_usd, 2),
            "O_eur"          : round(sell_eur, 2),
            "total_eur"      : round(total_eur, 2),
            "XDWD_eur"       : round(buy_eur, 2),
            "etf_shares"     : round(etf_shares, 4),
            "etf_shares_full": int(etf_shares),
            "eurusd"         : round(eurusd, 4),
        }

    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Kurse: {e}")
        sys.exit(1)


# ── Persistenz: bestes Ergebnis ────────────────────────────────────────────────
def load_best() -> int:
    try:
        with open(BEST_FILE) as f:
            return json.load(f)["best"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return 0


def save_best(value: int, timestamp: str):
    with open(BEST_FILE, "w") as f:
        json.dump({"best": value, "updated": timestamp}, f, indent=2)


# ── Persistenz: Verlauf ────────────────────────────────────────────────────────
def append_history(data: dict):
    history = []
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    history.append(data)

    # Maximal 500 Einträge behalten (≈ ~3 Monate à 30-Min-Intervall)
    if len(history) > 500:
        history = history[-500:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


# ── Telegram ───────────────────────────────────────────────────────────────────
def send_telegram(text: str):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("ℹ️  Kein Telegram-Token gesetzt – nur Konsolenausgabe.")
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        json={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"⚠️  Telegram-Fehler {resp.status_code}: {resp.text}")


# ── Nachrichtentext ────────────────────────────────────────────────────────────
def format_message(data: dict, prev_best: int, is_morning: bool) -> str:
    is_new_max = data["etf_shares_full"] > prev_best

    if is_new_max:
        header = f"🏆 *NEUES MAXIMUM* (+{data['etf_shares_full'] - prev_best} Anteile)\n\n"
    elif is_morning:
        header = "🌅 *Tages-Update*\n\n"
    else:
        header = "📊 *Kurs-Check*\n\n"

    return (
        f"{header}"
        f"🕐 {data['timestamp']}\n\n"
        f"📈 *Realty Income (O)*\n"
        f"   `{data['O_usd']} USD`  →  `{data['O_eur']} EUR`\n"
        f"   60 Stück = `{data['total_eur']} EUR`\n\n"
        f"📉 *Xtrackers MSCI World (XDWD)*\n"
        f"   `{data['XDWD_eur']} EUR`\n\n"
        f"💱 EUR/USD: `{data['eurusd']}`\n\n"
        f"✅ *Kaufbare ETF-Anteile: {data['etf_shares_full']}*\n"
        f"   _(exakt: {data['etf_shares']})_\n\n"
        f"📌 Bisheriges Maximum: {prev_best} Anteile"
    )


# ── Hauptprogramm ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🚀 Tracker läuft – {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    data      = get_prices()
    prev_best = load_best()
    is_new_max = data["etf_shares_full"] > prev_best
    is_morning = datetime.now(timezone.utc).hour == MORNING_HOUR_UTC

    msg = format_message(data, prev_best, is_morning)
    print(msg.replace("*", "").replace("`", ""))  # sauber in Konsole

    # Nachricht senden wenn: neues Maximum ODER erster Run des Tages ODER manueller Test
    force = os.environ.get("FORCE_NOTIFY", "").lower() == "true"
    if is_new_max or is_morning or force:
        send_telegram(msg)
        print("✉️  Telegram-Nachricht gesendet." if TG_TOKEN else "")

    # Verlauf immer speichern
    append_history(data)

    # Neues Maximum persistieren + ins Repo committen
    if is_new_max:
        save_best(data["etf_shares_full"], data["timestamp"])
        print(f"🏆 Neues Maximum: {data['etf_shares_full']} Anteile – best.json aktualisiert.")
