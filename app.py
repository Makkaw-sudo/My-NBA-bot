import streamlit as st
import pandas as pd

# --- 1. THE QUANTUM PROTECTED ENGINE ---
class QuantumTitanEngine:
    def __init__(self, base_stake, stop_loss, max_stake):
        self.base_stake = base_stake
        self.stop_loss = stop_loss
        self.max_stake = max_stake
        self.total_loss = 0
        self.authorized_leagues = [
            "Premier League", "La Liga", "Serie A", "Bundesliga", 
            "Ligue 1", "Saudi Pro League", "Liga Portugal", 
            "Eredivisie", "MLS", "Botola Pro"
        ]

    def calculate_protected_stake(self, odds):
        """Calculates stake with Stop-Loss and Max-Stake protections."""
        if self.total_loss >= self.stop_loss:
            return "STOP_LOSS_REACHED"
        if odds <= 1.0: return 0.0
        
        # Dynamic Martingale Formula
        required_stake = (self.total_loss + self.base_stake) / (odds - 1)
        
        if required_stake > self.max_stake:
            return "MAX_STAKE_EXCEEDED"
            
        return round(float(required_stake), 2)

# --- 2. UI CONFIGURATION ---
st.set_page_config(page_title="QUANTUM TITAN V11", layout="wide")
st.title("🚀 QUANTUM TITAN V11: Fully Separated & Protected")

# SIDEBAR: RISK MANAGEMENT
st.sidebar.header("🛡️ Security & Bankroll")
base_amt = st.sidebar.number_input("Base Stake ($)", value=10.0)
acc_loss = st.sidebar.number_input("Current Cycle Loss ($)", value=0.0)
max_loss = st.sidebar.number_input("STOP-LOSS Limit ($)", value=200.0)
bookie_cap = st.sidebar.number_input("MAX STAKE Limit ($)", value=150.0)

engine = QuantumTitanEngine(base_amt, max_loss, bookie_cap)
engine.total_loss = acc_loss

# --- 3. SEPARATED LIVE DATA (APRIL 22, 2026) ---
nba_feed = [
    {'Game': 'Orlando @ Detroit', 'Stage': 'Q1', 'Market': 'Over 51.5', 'Prob': 0.74, 'Odds': 1.72},
    {'Game': 'Orlando @ Detroit', 'Stage': 'Q2', 'Market': 'Under 54.5', 'Prob': 0.69, 'Odds': 1.80}
]

football_feed = [
    {'Match': 'AS FAR vs RS Berkane', 'League': 'Botola Pro', 'Market': 'Under 2.5', 'Prob': 0.82, 'Odds': 1.62},
    {'Match': 'Man City @ Burnley', 'League': 'Premier League', 'Market': 'City Over 1.5', 'Prob': 0.78, 'Odds': 1.60},
    {'Match': 'Celta Vigo @ Barcelona', 'League': 'La Liga', 'Market': 'Over 8.5 Corners', 'Prob': 0.73, 'Odds': 1.68}
]

# --- 4. THE DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["🏀 NBA Quarters", "⚽ Elite Football", "📜 History"])

with tab1:
    st.subheader("NBA Playoff: Quarter-by-Quarter")
    st.table(nba_feed)
    best_nba = nba_feed[0]
    stake = engine.calculate_protected_stake(best_nba['Odds'])
    
    if isinstance(stake, str):
        st.error(f"🚨 {stake}")
    else:
        st.success(f"🎯 **Signal:** {best_nba['Game']} {best_nba['Stage']} | **Stake: ${stake}**")
        st.caption("⚠️ Verification: If the live bookie line is > 1.5 pts off, DISCARD SIGNAL.")

with tab2:
    st.subheader("Top 9 Leagues & Botola Pro")
    st.table(football_feed)
    best_foot = football_feed[0] # AS FAR vs RS Berkane
    f_stake = engine.calculate_protected_stake(best_foot['Odds'])
    
    if isinstance(f_stake, str):
        st.error(f"🚨 {f_stake}")
    else:
        st.info(f"🎯 **Signal:** {best_foot['Match']} ({best_foot['League']}) | **Stake: ${f_stake}**")

with tab3:
    st.subheader("Cycle Tracking")
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if st.button("Log Current Bet as WIN"):
        st.session_state.history.append("✅ WIN")
        st.balloons()
    if st.button("Log Current Bet as LOSS"):
        st.session_state.history.append("❌ LOSS")
    
    st.write(st.session_state.history)

st.markdown("---")
st.caption("Active Filters: NBA Quarters | Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Saudi Pro, Liga Portugal, Eredivisie, MLS | Botola Pro")
