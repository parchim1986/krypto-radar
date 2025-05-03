### KryptoRadar mit CoinMarketCap, Preisverlauf & Mail-Benachrichtigung (via GMX)

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="KryptoRadar 🛰️", layout="centered")
st.title("🪙 KryptoRadar – Neue Coins & Alarm bei Bewegungen")

# Auto-Refresh alle 60 Sekunden
st_autorefresh(interval=60000, key="refresh")

# 🔌 Lade Secrets aus .streamlit/secrets.toml
CMC_API_KEY = st.secrets["CMC_API_KEY"]
EMAIL_HOST = st.secrets["EMAIL_HOST"]
EMAIL_PORT = st.secrets["EMAIL_PORT"]
EMAIL_USER = st.secrets["EMAIL_USER"]
EMAIL_PASS = st.secrets["EMAIL_PASS"]

# Mail senden (optional über Schalter aktiviert)
def send_email_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = "parchim1986@gmx.de"
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        st.error(f"Fehler beim E-Mail-Versand: {e}")

# Mailversand aktivieren/deaktivieren
send_emails = st.toggle("📩 Benachrichtigungen per Mail aktivieren")

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

            # Kriterien für Alarm
            if send_emails and (change > 15 or marketcap < 5_000_000 or volume > 10_000_000):
                msg = f"Coin: {name} ({symbol})\nPreis: {price:.4f} $\n24h: {change:.2f} %\nMarketCap: {marketcap:,.0f} $\nVolumen: {volume:,.0f} $\n{link}"
                send_email_alert("🔔 KryptoRadar Alarm", msg)

            st.markdown("---")

    except Exception as e:
        st.error("Fehler beim Laden der CoinMarketCap-Daten.")
        st.exception(e)

st.caption("Datenquelle: CoinMarketCap API – Nur zu Informationszwecken. Keine Finanzberatung.")


