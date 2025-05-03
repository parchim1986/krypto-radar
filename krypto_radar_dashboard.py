### KryptoRadar mit CoinMarketCap, Preisverlauf & Telegram-Benachrichtigung

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="KryptoRadar 🛰️", layout="centered")
st.title("🪙 KryptoRadar – Neue Coins & Telegram-Alarm")

# Auto-Refresh alle 60 Sekunden
st_autorefresh(interval=60000, key="refresh")

# Secrets laden
CMC_API_KEY = st.secrets["CMC_API_KEY"]
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

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

# Benutzer-Schalter
send_telegram = st.toggle("📲 Telegram-Benachrichtigungen aktivieren")

# CoinMarketCap API Setup
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC_API_KEY}
params = {"start": "1", "limit": "10", "sort": "date_added", "convert": "USD"}

with st.spinner("🔍 Lade neue Coins von CoinMarketCap..."):
    try:
        response = requests.get(CMC_URL, headers=headers, params=params)
        data = response.json()["data"]

        for coin in data:
            name = coin["name"]
            symbol = coin["symbol"]
            price = coin["quote"]["USD"]["price"]
            marketcap = coin["quote"]["USD"]["market_cap"]
            volume = coin["quote"]["USD"]["volume_24h"]
            change = coin["quote"]["USD"]["percent_change_24h"]
            link = f"https://coinmarketcap.com/currencies/{coin['slug']}"

            st.markdown(f"**[{name} ({symbol})]({link})**")
            st.write(f"💲 Preis: {price:.4f} $ | 💼 MarketCap: {int(marketcap):,} $")
            st.write(f"📈 Volumen (24h): {int(volume):,} $ | Veränderung: {change:.2f} %")

            # Simulierter Preisverlauf
            st.write("📉 Simulierter Preisverlauf der letzten 7 Tage (in $):")
            fig, ax = plt.subplots()
            fake_prices = [price * (1 + (i - 3) * 0.01) for i in range(7)]
            ax.plot(range(1, 8), fake_prices, marker='o')
            ax.set_xticks(range(1, 8))
            ax.set_xticklabels([f"Tag {i}" for i in range(1, 8)])
            ax.set_ylabel("Preis ($)")
            ax.set_title(f"{symbol} – 7 Tage Preisentwicklung (simuliert)")
            ax.grid(True)
            st.pyplot(fig)

            # Alarm bei bestimmten Bedingungen
            if send_telegram and (change > 15 or marketcap < 5_000_000 or volume > 10_000_000):
                message = (
                    f"🚨 *KryptoRadar Alarm* 🚨\n"
                    f"*{name} ({symbol})*\n"
                    f"💰 Preis: {price:.4f} $\n"
                    f"📊 24h Änderung: {change:.2f}%\n"
                    f"🏦 MarketCap: {int(marketcap):,} $\n"
                    f"💸 Volumen (24h): {int(volume):,} $\n"
                    f"🔗 [Zum Coin]({link})"
                )
                send_telegram_alert(message)

            st.markdown("---")

    except Exception as e:
        st.error("Fehler beim Laden der CoinMarketCap-Daten.")
        st.exception(e)

st.caption("Datenquelle: CoinMarketCap API – Nur zu Informationszwecken. Keine Finanzberatung.")
