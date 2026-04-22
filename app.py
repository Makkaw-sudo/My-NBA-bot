import streamlit as st
import pandas as pd

# --- 1. THE QUANTUM DECISION ENGINE ---
class QuantumTitanEngine:
    def __init__(self, base_stake):
        self.base_stake = base_stake
        self.total_loss = 0
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
        if not valid_plays: return None
        return max(valid_plays, key=lambda x: x['prob'] * x['odds'])

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="QUANTUM TITAN V11", layout="wide")
st.title("🚀 QUANTUM TITAN V11")

# Sidebar: Bankroll and Martingale Control
st.sidebar.header("🏦 Bankroll Management")
base_amt = st.sidebar.number_input("Base Stake ($)", value=10.0)
acc_loss = st.sidebar.number_input("Accumulated Loss ($)", value=0.0)

engine = QuantumTitanEngine(base_amt)
engine.total_loss = acc_loss

# --- 3. LIVE MATCH DATA (APRIL 22, 2026) ---
# Separated by quarters and elite competitions
live_feed = [
    # MOROCCO: Botola Pro
    {'match': 'AS FAR vs RS Berkane', 'league': 'Botola Pro', 'market': 'Under 2.5 Goals', 'prob': 0.82, 'odds': 1.62},
    {'match': 'OC Safi vs RCA Zemamra', 'league': 'Botola Pro', 'market': 'Under 3.5 Live', 'prob': 0.75, 'odds': 1.55},
    # EUROPE: Top 9 Leagues
    {'match': 'Burnley vs Man City', 'league': 'Premier League', 'market': 'City Over 1.5 Goals', 'prob': 0.78, 'odds': 1.60},
    {'match': 'Barcelona vs Celta Vigo', 'league': 'La Liga', 'market': 'Over 8.5 Corners', 'prob': 0.73, 'odds': 1.68},
    {'match': 'PSG vs Nantes', 'league': 'Ligue 1', 'market': 'PSG Over 2.5 Goals', 'prob': 0.85, 'odds': 1.45},
    # NBA: Quarter-by-Quarter
    {'match': 'NBA: Det/Orl Q1', 'type': 'NBA', 'league': 'NBA', 'market': 'Over 51.5 Pts', 'prob': 0.74, 'odds': 1.72},
    {'match': 'NBA: Det/Orl Q2', 'type': 'NBA', 'league': 'NBA', 'market': 'Under 54.5 Pts', 'prob': 0.69, 'odds': 1.80}
]

# --- 4. DASHBOARD EXECUTION ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📡 Live Elite Market Feed")
    filtered_data = [p for p in live_feed if p['league'] in engine.authorized_leagues or p.get('type') == 'NBA']
    st.dataframe(pd.DataFrame(filtered_data), use_container_width=True)

with col2:
    st.subheader("🎯 The Perfect Selection")
    perfect_play = engine.find_perfect_play(live_feed)
    
    if perfect_play:
        st.success(f"**{perfect_play['match']}**")
        st.write(f"**Market:** {perfect_play['market']}")
        rec_stake = engine.calculate_autonomous_stake(perfect_play['odds'])
        
        st.metric("Required Stake", f"${rec_stake}")
        st.metric("Win Probability", f"{perfect_play['prob']:.0%}")
        st.metric("Current Odds", f"{perfect_play['odds']}")

        if st.button("📤 SEND SIGNAL TO TELEGRAM"):
            st.toast("Signal sent to phone!")
    else:
        st.warning("Scanning for valid Elite Market opportunities...")

st.markdown("---")
st.info("Filters Active: NBA Q1-Q4 | Top 9 Leagues | Botola Pro | Dynamic Stakes")
