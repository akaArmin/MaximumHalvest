"""
Historische Analyse: Realty Income (O) → UDIV Tausch-Tracker
Berechnet wie viele UDIV-Anteile man aus 60 O-Aktien bekommen hätte.

Ausführen:
    pip install yfinance pandas
    python historical_analysis.py
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# ── Konfiguration ──────────────────────────────────────────────
SHARES_SELL = 60
SELL_TICKER = "O"        # Realty Income – NYSE (USD)
BUY_TICKER  = "UDIV.DE"  # Global X SuperDividend – Xetra (EUR)
FX_TICKER   = "EURUSD=X"
PERIOD_DAYS = 365


# ── Daten laden ────────────────────────────────────────────────
print("Lade Kursdaten...")

end   = datetime.today()
start = end - timedelta(days=PERIOD_DAYS)

def get_close(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)["Close"]
    # Neuere yfinance-Versionen geben einen DataFrame zurück – in Series umwandeln
    if isinstance(df, pd.DataFrame):
        df = df.iloc[:, 0]
    return df

o    = get_close(SELL_TICKER, start, end)
udiv = get_close(BUY_TICKER,  start, end)
fx   = get_close(FX_TICKER,   start, end)

# Auf gemeinsame Handelstage ausrichten (forward-fill für fehlende Tage)
df = pd.DataFrame({"O_usd": o, "UDIV_eur": udiv, "EURUSD": fx})
df = df.ffill().dropna()

# ── Berechnung ─────────────────────────────────────────────────
df["O_eur"]         = df["O_usd"] / df["EURUSD"]
df["Erloes_eur"]    = df["O_eur"] * SHARES_SELL
df["Anteile_exakt"] = df["Erloes_eur"] / df["UDIV_eur"]
df["Anteile_ganz"]  = df["Anteile_exakt"].astype(int)

# ── Auswertung ─────────────────────────────────────────────────
best_row  = df["Anteile_ganz"].idxmax()
worst_row = df["Anteile_ganz"].idxmin()
current   = df.iloc[-1]

print("\n" + "="*55)
print("  Realty Income (O) → UDIV  |  Letztes Jahr")
print("="*55)

print(f"\n📅 Zeitraum: {df.index[0].date()} – {df.index[-1].date()}")
print(f"   Handelstage: {len(df)}")

print(f"\n🏆 MAXIMUM  am {best_row.date()}")
row = df.loc[best_row]
print(f"   O:          {row['O_usd']:.2f} USD  ({row['O_eur']:.2f} EUR)")
print(f"   UDIV:       {row['UDIV_eur']:.2f} EUR")
print(f"   EUR/USD:    {row['EURUSD']:.4f}")
print(f"   Erlös:      {row['Erloes_eur']:.2f} EUR")
print(f"   ➜ {int(row['Anteile_ganz'])} ganze Anteile  (exakt: {row['Anteile_exakt']:.2f})")

print(f"\n📉 MINIMUM  am {worst_row.date()}")
row = df.loc[worst_row]
print(f"   O:          {row['O_usd']:.2f} USD  ({row['O_eur']:.2f} EUR)")
print(f"   UDIV:       {row['UDIV_eur']:.2f} EUR")
print(f"   EUR/USD:    {row['EURUSD']:.4f}")
print(f"   Erlös:      {row['Erloes_eur']:.2f} EUR")
print(f"   ➜ {int(row['Anteile_ganz'])} ganze Anteile  (exakt: {row['Anteile_exakt']:.2f})")

print(f"\n📊 HEUTE  ({df.index[-1].date()})")
print(f"   O:          {current['O_usd']:.2f} USD  ({current['O_eur']:.2f} EUR)")
print(f"   UDIV:       {current['UDIV_eur']:.2f} EUR")
print(f"   EUR/USD:    {current['EURUSD']:.4f}")
print(f"   Erlös:      {current['Erloes_eur']:.2f} EUR")
print(f"   ➜ {int(current['Anteile_ganz'])} ganze Anteile  (exakt: {current['Anteile_exakt']:.2f})")

avg = df["Anteile_ganz"].mean()
print(f"\n📈 Durchschnitt (1 Jahr): {avg:.1f} Anteile")
print(f"   Aktuelle Position:      {'✅ ÜBER Durchschnitt' if current['Anteile_ganz'] > avg else '⏳ unter Durchschnitt'}")

print("="*55)

# ── CSV Export ─────────────────────────────────────────────────
out = df[["O_usd", "O_eur", "EURUSD", "UDIV_eur", "Erloes_eur", "Anteile_ganz", "Anteile_exakt"]].copy()
out.index.name = "Datum"
out.to_csv("verlauf.csv", float_format="%.4f")
print("\n💾 Verlauf gespeichert: verlauf.csv")
