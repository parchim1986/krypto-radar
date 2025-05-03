### KryptoRadar – Neue Coins mit deutscher Beschreibung, Blockchain & Marktkapitalisierung

import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="KryptoRadar 🛰️", layout="centered")
st.title("🪙 KryptoRadar – Neue Coins mit Beschreibung, Blockchain & MarketCap")

# Auto-Refresh alle 60 Sekunden
st_autorefresh(interval=60000, key="refresh")

# Secrets laden
CMC_API_KEY = st.secrets.get("CMC_API_KEY", "")
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# Session State für gesendete Coins
if "notified_coins" not in st.session_state:
    st.session_state.notified_coins = set()

# Telegram-Funktion

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Telegram-Fehler: {e}")

# Google Translate API (frei) nutzen

def simple_translate(text, target_lang="DE"):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": target_lang.lower(),
            "dt": "t",
            "q": text
        }
        r = requests.get(url, params=params)
        return r.json()[0][0][0]
    except:
        return text

send_telegram = st.toggle("📲 Telegram-Benachrichtigungen aktivieren")
st.markdown("Nur neue Coins – mit Blockchain, Marktkapitalisierung & deutscher Beschreibung")

used_fallback = False
coins = []
try:
    CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"start": "1", "limit": "20", "sort": "date_added", "convert": "USD"}
    response = requests.get(CMC_URL, headers=headers, params=params)
    result = response.json()
    if "data" not in result:
        raise Exception(result.get("status", {}).get("error_message", "CMC Antwort ohne Daten"))
    coins = result["data"]
except Exception as e:
    st.warning(f"⚠️ CoinMarketCap fehlgeschlagen: {e}\n→ Wechsle zu CoinGecko...")
    used_fallback = True
    try:
        gecko_url = "https://api.coingecko.com/api/v3/coins/list?include_platform=false"
        coins = requests.get(gecko_url).json()[-20:]
    except Exception as gerr:
        st.error("CoinGecko ebenfalls nicht erreichbar.")
        st.stop()

for coin in coins:
    try:
        if used_fallback:
            name = coin["name"]
            symbol = coin["symbol"]
            link = f"https://www.coingecko.com/de/munze/{coin['id']}"
            coin_id = coin["id"]
            short_desc = "Neu gelisteter Coin auf CoinGecko. Keine Beschreibung verfügbar."
            price = "?"
            market_cap = "?"
            platform = "?"
        else:
            name = coin["name"]
            symbol = coin["symbol"]
            link = f"https://coinmarketcap.com/currencies/{coin['slug']}"
            coin_id = coin["id"]
            price = coin["quote"]["USD"]["price"]
            market_cap = coin["quote"]["USD"]["market_cap"]

            # Beschreibung & Plattform laden
            info_url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?id={coin_id}"
            desc_data = requests.get(info_url, headers=headers).json()
            raw_desc = desc_data.get("data", {}).get(str(coin_id), {}).get("description", "Keine Beschreibung verfügbar.")
            platform = desc_data.get("data", {}).get(str(coin_id), {}).get("platform", {}).get("name", "Unbekannt")
            short_en = raw_desc.strip().split(".")[0][:400] + "..."
            short_desc = simple_translate(short_en)

        if coin_id in st.session_state.notified_coins:
            continue

        st.markdown(f"### 🆕 [{name} ({symbol})]({link})")
        st.write(f"💲 Einstiegspreis: {price if price == '?' else f'{price:.6f} $'}")
        st.write(f"🧱 Blockchain: {platform}")
        st.write(f"💼 Marktkapitalisierung: {market_cap if market_cap == '?' else f'{market_cap:,.2f} $'}")
        st.write(short_desc)

        if send_telegram:
            message = (
                f"🚀 *Neuer Coin entdeckt!*\n"
                f"*{name} ({symbol})*\n"
                f"💲 Einstiegspreis: {price if price == '?' else f'{price:.6f} $'}\n"
                f"🧱 Blockchain: {platform}\n"
                f"💼 Marktkapitalisierung: {market_cap if market_cap == '?' else f'{market_cap:,.2f} $'}\n"
                f"{short_desc}\n"
                f"🔗 [Zum Coin]({link})"
            )
            send_telegram_alert(message)

        st.session_state.notified_coins.add(coin_id)
        st.markdown("---")
    except Exception as inner:
        st.error(f"Fehler beim Verarbeiten eines Coins: {inner}")

st.caption("Datenquelle: CoinMarketCap & CoinGecko. Übersetzung via Google Translate API. Keine Finanzberatung.")
