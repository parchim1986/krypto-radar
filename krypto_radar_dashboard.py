### KryptoRadar Dashboard (Streamlit-Prototyp)
# Zeigt neue Coins, aktuelle Preise, Volumen und Trend-Infos

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="KryptoRadar 🛰️", layout="centered")
st.title("🪙 KryptoRadar – Entdecke neue Coins & Trends")

# API URL von CoinGecko für neue Coins (Placeholder)
COIN_API_URL = "https://api.coingecko.com/api/v3/coins/markets"

params = {
    "vs_currency": "usd",
    "order": "market_cap_asc",
    "per_page": 20,
    "page": 1,
    "sparkline": False,
    "price_change_percentage": "24h"
}

with st.spinner("🔍 Lade neue Coins..."):
    try:
        response = requests.get(COIN_API_URL, params=params)
        data = response.json()
        df = pd.DataFrame(data)

        df = df[[
            "name", "symbol", "current_price", "market_cap",
            "total_volume", "price_change_percentage_24h",
            "image", "id"
        ]]

        df["link"] = df["id"].apply(lambda x: f"https://www.coingecko.com/en/coins/{x}")

        st.subheader("🆕 Neue Coins mit kleiner Marktkapitalisierung")
        for _, row in df.iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(row["image"], width=40)
            with col2:
                st.markdown(f"**[{row['name']} ({row['symbol'].upper()})]({row['link']})**")
                st.write(f"💲 Preis: {row['current_price']} $ | 💼 MarketCap: {int(row['market_cap']):,} $")
                st.write(f"📈 Volumen: {int(row['total_volume']):,} $ | 24h: {round(row['price_change_percentage_24h'], 2)} %")
                st.markdown("---")

    except Exception as e:
        st.error("Fehler beim Laden der Daten. API möglicherweise nicht verfügbar.")
        st.exception(e)

st.caption("Datenquelle: CoinGecko API – Nur zu Informationszwecken. Keine Finanzberatung.")
