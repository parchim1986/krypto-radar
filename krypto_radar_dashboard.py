### KryptoRadar – Neue Coins mit Erklärung & einmaliger Telegram-Benachrichtigung

import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="KryptoRadar 🛰️", layout="centered")
st.title("🪙 KryptoRadar – Nur brandneue Coins + Telegram-Info")

# Automatisch alle 60 Sekunden aktualisieren
st_autorefresh(interval=60000, key="refresh")

# Secrets laden
CMC_API_KEY = st.secrets["CMC_API_KEY"]
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# Session State für einmalige Telegram-Meldung
if "notified_coins" not in st.session_state:
    st.session_state.notified_coins = set()

# Telegram-Nachricht senden
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
        st.error(f"Fehler beim Senden an Telegram: {e}")

# CMC API Setup
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC_API_KEY}
params = {"start": "1", "limit": "25", "sort": "date_added", "convert": "USD"}

st.markdown("Hier erscheinen nur **neue Coins**, jeweils nur einmal – mit Beschreibung.")
send_telegram = st.toggle("📲 Telegram-Benachrichtigungen aktivieren")

with st.spinner("🔍 Lade neue Coins von CoinMarketCap..."):
    try:
        response = requests.get(CMC_URL, headers=headers, params=params)
        data = response.json()["data"]

        for coin in data:
            coin_id = coin["id"]
            name = coin["name"]
            symbol = coin["symbol"]
            link = f"https://coinmarketcap.com/currencies/{coin['slug']}"
            description_url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?id={coin_id}"

            # Nur anzeigen, wenn noch nicht verarbeitet
            if coin_id in st.session_state.notified_coins:
                continue

            st.markdown(f"### 🆕 [{name} ({symbol})]({link})")

            # Beschreibung laden
            desc_response = requests.get(description_url, headers=headers)
            desc_data = desc_response.json()
            description = desc_data.get("data", {}).get(str(coin_id), {}).get("description", "Keine Beschreibung verfügbar.")

            short_desc = description.strip().split(".")[0][:400] + "..."
            st.write(short_desc)

            # Telegram senden (einmalig)
            if send_telegram:
                msg = (
                    f"🚀 *Neuer Coin entdeckt!*\n"
                    f"*{name} ({symbol})*\n"
                    f"{short_desc}\n"
                    f"🔗 [Mehr erfahren]({link})"
                )
                send_telegram_alert(msg)

            # Als verarbeitet markieren
            st.session_state.notified_coins.add(coin_id)
            st.markdown("---")

    except Exception as e:
        st.error("Fehler beim Abrufen von CoinMarketCap-Daten.")
        st.exception(e)

st.caption("Nur neue Coins. Datenquelle: CoinMarketCap API. Keine Finanzberatung.")

