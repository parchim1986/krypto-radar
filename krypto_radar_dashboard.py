### KryptoRadar – Neue Coins mit CoinMarketCap + CoinGecko Fallback

import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="KryptoRadar 🛰️", layout="centered")
st.title("🪙 KryptoRadar – Neue Coins & Telegram mit CMC + CoinGecko Backup")

# Auto-Refresh alle 60 Sekunden
st_autorefresh(interval=60000, key="refresh")

# Lade Secrets
CMC_API_KEY = st.secrets.get("CMC_API_KEY", "")
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# Session-State für gesendete Coins
if "notified_coins" not in st.session_state:
    st.session_state.notified_coins = set()

# Telegram senden
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

send_telegram = st.toggle("📲 Telegram aktivieren")
st.markdown("Nur neue Coins – automatisch erkannt. CMC mit CoinGecko-Fallback.")

# Erst CMC versuchen
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
        coins = requests.get(gecko_url).json()[-20:]  # nur die letzten 20
    except Exception as gerr:
        st.error("CoinGecko ebenfalls nicht erreichbar.")
        st.stop()

# Verarbeitung & Anzeige
for coin in coins:
    try:
        if used_fallback:
            name = coin["name"]
            symbol = coin["symbol"]
            link = f"https://www.coingecko.com/en/coins/{coin['id']}"
            coin_id = coin["id"]
            short_desc = "Neu gelisteter Coin auf CoinGecko. Beschreibung nicht verfügbar."
        else:
            name = coin["name"]
            symbol = coin["symbol"]
            link = f"https://coinmarketcap.com/currencies/{coin['slug']}"
            coin_id = coin["id"]
            # Beschreibung laden
            info_url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?id={coin_id}"
            desc = requests.get(info_url, headers=headers).json()
            full = desc.get("data", {}).get(str(coin_id), {}).get("description", "Keine Beschreibung verfügbar.")
            short_desc = full.strip().split(".")[0][:400] + "..."

        if coin_id in st.session_state.notified_coins:
            continue

        st.markdown(f"### 🆕 [{name} ({symbol})]({link})")
        st.write(short_desc)

        if send_telegram:
            message = f"🚀 *Neuer Coin entdeckt!*\n*{name} ({symbol})*\n{short_desc}\n🔗 [Zum Coin]({link})"
            send_telegram_alert(message)

        st.session_state.notified_coins.add(coin_id)
        st.markdown("---")
    except Exception as inner:
        st.error(f"Fehler beim Verarbeiten eines Coins: {inner}")

st.caption("Daten: CoinMarketCap & CoinGecko. Keine Finanzberatung.")


