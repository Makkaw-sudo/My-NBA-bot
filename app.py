import streamlit as st
import pandas as pd

# --- 1. CORE ENGINE ---
class QuantumTitanEngine:
    def __init__(self, base_stake, stop_loss, max_stake):
        self.base_stake = base_stake
        self.stop_loss = stop_loss
        self.max_stake = max_stake
        self.total_loss = 0

    def calculate_results(self, odds):
        """Calculates stake and next-step recovery logic."""
        if self.total_loss >= self.stop_loss:
            return None, "STOP-LOSS HIT"
        if odds <= 1.0: return 0.0, 0.0
        
        stake = (self.total_loss + self.base_stake) / (odds - 1)
        
        if stake > self.max_stake:
            return None, "LIMIT EXCEEDED"
            
        payout = stake * odds
        return round(float(stake), 2), round(float(payout), 2)

# --- 2. UI SETUP ---
st.set_page_config(page_title="QUANTUM TITAN V11", layout="wide")
st.title("🚀 QUANTUM TITAN V11: Overs Strategy Only")

# SIDEBAR: Risk Management
st.sidebar.header("🛡️ Risk & Recovery")
base_amt = st.sidebar.number_input("Base Stake ($)", value=10.0)
acc_loss = st.sidebar.number_input("Current Cycle Loss ($)", value=0.0)
max_loss = st.sidebar.number_input("Stop-Loss Limit ($)", value=200.0)
bookie_cap = st.sidebar.number_input("Max Bet Limit ($)", value=150.0)

engine = QuantumTitanEngine(base_amt, max_loss, bookie_cap)
engine.total_loss = acc_loss

# --- 3. "OVERS ONLY" DATA FEEDS (April 22, 2026) ---
nba_feed = [
    {'match': 'Orlando @ Detroit', 'stage': 'Q1', 'market': 'Over 51.5 Pts', 'odds': 1.72},
    {'match': 'Phoenix @ OKC', 'stage': 'Q1', 'market': 'Over 53.5 Pts', 'odds': 1.68},
    {'match': 'Orlando @ Detroit', 'stage': 'Q2', 'market': 'Over 52.5 Pts', 'odds': 1.75}
]

football_feed = [
    {'match': 'Man City @ Burnley', 'league': 'Premier League', 'market': 'Total Goals Over 2.5', 'odds': 1.65},
    {'match': 'Celta Vigo @ Barcelona', 'league': 'La Liga', 'market': 'Total Corners Over 9.5', 'odds': 1.70},
    {'match': 'AS FAR vs RS Berkane', 'league': 'Botola Pro', 'market': 'Total Goals Over 1.5', 'odds': 1.58},
    {'match': 'PSG vs Nantes', 'league': 'Ligue 1', 'market': 'PSG Team Goals Over 2.5', 'odds': 1.82}
]

# --- 4. DISPLAY WITH INDIVIDUAL BETTING BARS ---
tab1, tab2 = st.tabs(["🏀 NBA Quarters (Overs)", "⚽ Elite Football (Overs)"])

def display_overs_bar(game_name, market, odds):
    """Generates a dedicated betting bar for an 'Over' market."""
    stake, payout = engine.calculate_results(odds)
    
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        with col1:
            st.markdown(f"**{game_name}**")
            st.markdown(f"<span style='color:green;'>📈 {market}</span>", unsafe_allow_html=True)
        with col2:
            st.metric("Odds", f"{odds}")
        with col3:
            if isinstance(stake, float):
                st.metric("Bet Stake", f"${stake}")
            else:
                st.error(stake)
        with col4:
            if isinstance(payout, float):
                st.metric("Payout on Win", f"${payout}")
                next_loss = round(acc_loss + stake, 2)
                st.warning(f"If Loss: Next Cycle Loss = ${next_loss}")
        st.markdown("---")

with tab1:
    st.subheader("NBA Playoff: Pace-Based Overs")
    for game in nba_feed:
        display_overs_bar(game['match'], f"{game['stage']} {game['market']}", game['odds'])

with tab2:
    st.subheader("Elite Football: High-Volume Offensive Markets")
    for match in football_feed:
        display_overs_bar(match['match'], f"{match['league']} {match['market']}", match['odds'])

# HISTORY LOG
st.subheader("📜 Cycle History")
if 'log' not in st.session_state: st.session_state.log = []
c1, c2 = st.columns(2)
if c1.button("✅ WIN: Reset to Base Stake"):
    st.session_state.log.append("WIN: Cycle Cleared")
    st.balloons()
if c2.button("❌ LOSS: Trigger Martingale"):
    st.session_state.log.append(f"LOSS: Active Loss ${acc_loss}")
st.write(st.session_state.log)
