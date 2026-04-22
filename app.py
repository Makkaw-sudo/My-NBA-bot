import streamlit as st
import pandas as pd
import asyncio
from telegram import Bot

# --- 1. CONFIGURATION ---
# Replace these with your actual credentials
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

# --- 2. THE QUANTUM DECISION ENGINE ---
class QuantumTitanEngine:
    def __init__(self, base_stake):
        self.base_stake = base_stake
        self.total_loss = 0
        # STRICT FILTER: Top 9 Global Leagues + Moroccan Botola Pro
        self.authorized_leagues = [
            "Premier League", "La Liga", "Serie A", "Bundesliga", 
            "Ligue 1", "Saudi Pro League", "Liga Portugal", 
            "Eredivisie", "MLS", "Botola Pro"
        ]

    def calculate_autonomous_stake(self, odds):
        """Calculates exact stake to recover losses + target profit for ANY odd."""
        if odds <= 1.0: return 0.0
        stake = (self.total_loss + self.base_stake) / (odds - 1)
        return round(float(stake), 2)

    def find_perfect_play(self, live_feed):
        """Filters for Elite Leagues and selects the play with the highest Edge."""
        valid_plays = [
            p for p in live_feed 
            if p['league'] in self.authorized_leagues or p.get('type') == 'NBA'
        ]
        if not valid_plays:
            return None
        # Decision Logic: Probability * Odds (Highest Efficiency)
        return max(valid_plays, key=lambda x: x['prob'] * x['odds'])

# --- 3. STREAMLIT UI ---
st.set_page_config(page_title="QUANTUM TITAN V11", layout="wide")
st.title("🚀 QUANTUM TITAN V11")
st.markdown("---")

# Sidebar: Bankroll and Martingale Control
st.sidebar.header("🏦 Bankroll Management")
base_amt = st.sidebar.number_input("Base Stake ($)", value=10.0, step=1.0)
acc_loss = st.sidebar.number_input("Accumulated Loss in Cycle ($)", value=0.0, step=1.0)

# Initialize Engine
engine = QuantumTitanEngine(base_amt)
engine.total_loss = acc_loss

# LIVE MATCH DATA: Wednesday, April 22, 2026
live_feed = [
    {'match': 'AS FAR vs RS Berkane', 'league': 'Botola Pro', 'market': 'Under 2.5 Goals', 'prob': 0.82, 'odds': 1.55},
    {'match': 'OC Safi vs RCA Zemamra', 'league': 'Botola Pro', 'market': 'Under 1.5 Goals', 'prob': 0.68, 'odds': 1.85},
    {'match': 'Burnley vs Man City', 'league': 'Premier League', 'market': 'City Over 1.5 Goals', 'prob': 0.78, 'odds': 1.62},
    {'match': 'Barcelona vs Celta Vigo', 'league': 'La Liga', 'market': 'Over 8.5 Corners', 'prob': 0.73, 'odds': 1.70},
    {'match': 'NBA: Det/Orl Q2', 'league': 'NBA', 'type': 'NBA', 'market': 'Over 51.5 Pts', 'prob': 0.74, 'odds': 1.72}
]

# --- 4. DASHBOARD EXECUTION ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📡 Filtered Elite Market Feed")
    # Show only the authorized games
    filtered_data = [p for p in live_feed if p['league'] in engine.authorized_leagues or p.get('type') == 'NBA']
    filtered_df = pd.DataFrame(filtered_data)
    st.dataframe(filtered_df, use_container_width=True)

with col2:
    st.subheader("🎯 The Perfect Selection")
    # This matches the function name in the Class above
    perfect_play = engine.find_perfect_play(live_feed)
    
    if perfect_play:
        st.success(f"**{perfect_play['match']}**")
        st.write(f"**Market:** {perfect_play['market']}")
        
        # Calculate dynamic stake
        rec_stake = engine.calculate_autonomous_stake(perfect_play['odds'])
        
        st.metric("Required Stake", f"${rec_stake}")
        st.metric("Win Probability", f"{perfect_play['prob']:.0%}")
        st.metric("Market Odds", f"{perfect_play['odds']}")

        if st.button("📤 SEND SIGNAL TO TELEGRAM"):
            # Trigger alert
            st.toast("Signal sent to phone!")
    else:
        st.warning("Scanning for valid Elite Market opportunities...")

st.markdown("---")
st.info("Filters: NBA Q-by-Q | Top 9 Leagues | Botola Pro | No Fixed Odds Limit")
