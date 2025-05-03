### KryptoRadar Dashboard (CMC-Version mit sicherem API-Key & Auto-Refresh)
# Zeigt neue Coins, aktuelle Preise, Volumen und Trend-Infos

import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="KryptoRadar 🛰️", layout="centered")
st.title("🪙 KryptoRadar – Entdecke neue Coins & Trends")

# Auto-Refresh alle 60 Sekunden
st_autorefresh(interval=60000, key="refresh")

# CoinMarketCap API-Key sicher laden
API_KEY = st.secrets["CMC_API_KEY"]  # Definiert in .streamlit/secrets.toml
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": API_KEY
}

params = {
    "start": "1",
    "limit": "20",
    "sort": "date_added",
    "convert": "USD"
}

with st.spinner("🔍 Lade neue Coins von CoinMarketCap..."):
    try:
        response = requests.get(CMC_URL, headers=headers, params=params)
        data = response.json()["data"]
        df = pd.DataFrame([{
            "Name": coin["name"],
            "Symbol": coin["symbol"],
            "Preis ($)": coin["quote"]["USD"]["price"],
            "MarketCap ($)": coin["quote"]["USD"]["market_cap"],
            "Volumen (24h)": coin["quote"]["USD"]["volume_24h"],
            "Veränderung (24h %)": coin["quote"]["USD"]["percent_change_24h"],
            "Link": f"https://coinmarketcap.com/currencies/{coin['slug']}"
        } for coin in data])

        st.subheader("🆕 Neue Coins laut CoinMarketCap")
        for _, row in df.iterrows():
            st.markdown(f"**[{row['Name']} ({row['Symbol']})]({row['Link']})**")
            st.write(f"💲 Preis: {row['Preis ($)']:.4f} $ | 💼 MarketCap: {int(row['MarketCap ($)']):,} $")
            st.write(f"📈 Volumen (24h): {int(row['Volumen (24h)']):,} $ | Veränderung: {row['Veränderung (24h %)']:.2f} %")
            st.markdown("---")

    except Exception as e:
        st.error("Fehler beim Laden der Daten von CoinMarketCap.")
        st.exception(e)

st.caption("Datenquelle: CoinMarketCap API – Nur zu Informationszwecken. Keine Finanzberatung.")

