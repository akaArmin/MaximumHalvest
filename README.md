# 📊 Realty Income → MSCI World Tausch-Tracker

Verfolgt automatisch, wie viele **Global X SuperDividend (UVID)** Anteile du mit dem Erlös
aus dem Verkauf von **60 Realty Income (O)** Aktien kaufen könntest.

Benachrichtigt dich per **Telegram** sobald ein neues Maximum erreicht wird.

---

## Wie es funktioniert

```
GitHub Actions läuft Mo–Fr alle 30 Min (09:00–17:00 MEZ)
        ↓
tracker.py ruft Kurse via yfinance ab (O, XDWD, EUR/USD)
        ↓
Berechnet: ETF-Anteile = (60 × Kurs_O / EUR/USD) / Kurs_XDWD
        ↓
Bei neuem Maximum oder 09:00 Uhr → Telegram-Nachricht
        ↓
best.json + history.json werden ins Repo committed
```

---

## Einrichtung

### 1. Repository forken / klonen

Dieses Repo auf GitHub als **privates** Repository anlegen.

### 2. Telegram Bot erstellen

1. In Telegram **@BotFather** anschreiben
2. `/newbot` eingeben → Name & Username vergeben
3. **Token** kopieren (sieht so aus: `123456:ABC-DEF...`)
4. Den Bot einmal anschreiben (damit er dir schreiben darf)
5. **@userinfobot** anschreiben → deine **Chat-ID** notieren

### 3. Secrets in GitHub hinterlegen

`Repository → Settings → Secrets and variables → Actions → New repository secret`

| Secret-Name       | Wert                        |
|-------------------|-----------------------------|
| `TELEGRAM_TOKEN`  | Token von @BotFather        |
| `TELEGRAM_CHAT_ID`| deine Chat-ID von @userinfobot |

### 4. Actions aktivieren

`Repository → Actions → "I understand my workflows, go ahead and enable them"`

**Fertig!** Der Tracker läuft ab sofort automatisch. ✅

---

## Manuell testen

`Repository → Actions → Tausch-Tracker → Run workflow`

---

## Dateien

| Datei | Bedeutung |
|-------|-----------|
| `tracker.py` | Hauptscript: Kurse abrufen, berechnen, benachrichtigen |
| `.github/workflows/tracker.yml` | Zeitplan & Ausführung via GitHub Actions |
| `best.json` | Aktuelles Maximum (wird automatisch aktualisiert) |
| `history.json` | Verlauf aller Messungen (wird automatisch erstellt) |
| `requirements.txt` | Python-Abhängigkeiten |

---

## Konfiguration anpassen

In `tracker.py` ganz oben:

```python
SHARES_SELL = 60        # Anzahl O-Aktien
SELL_TICKER = "O"       # Realty Income
BUY_TICKER  = "XDWD.DE" # Global X SuperDividend
```

Cron-Zeitplan in `.github/workflows/tracker.yml`:
```yaml
- cron: '0,30 8-16 * * 1-5'  # alle 30 Min, Mo–Fr, 09–17 Uhr MEZ
```
