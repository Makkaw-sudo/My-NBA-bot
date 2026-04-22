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
        """Calculates stake, potential profit, and the loss to carry forward."""
        if self.total_loss >= self.stop_loss:
            return None, "STOP-LOSS HIT"
        
        # Calculate Martingale Stake
        stake = (self.total_loss + self.base_stake) / (odds - 1)
        
        if stake > self.max_stake:
            return None, "LIMIT EXCEEDED"
            
        payout = stake * odds
        return round(float(stake), 2), round(float(payout), 2)

# --- 2. UI SETUP ---
st.set_page_config(page_title="QUANTUM TITAN V11", layout="wide")
st.title("🚀 QUANTUM TITAN V11: Execution Dashboard")

# SIDEBAR: Risk Management
st.sidebar.header("🛡️ Risk & Recovery")
base_amt = st.sidebar.number_input("Base Stake ($)", value=10.0)
acc_loss = st.sidebar.number_input("Current Cycle Loss ($)", value=0.0)
max_loss = st.sidebar.number_input("Stop-Loss Limit ($)", value=200.0)
bookie_cap = st.sidebar.number_input("Max Bet Limit ($)", value=150.0)

engine = QuantumTitanEngine(base_amt, max_loss, bookie_cap)
engine.total_loss = acc_loss

# --- 3. SEPARATED MATCH DATA ---
nba_feed = [
    {'match': 'Orlando @ Detroit', 'stage': 'Q1', 'market': 'Over 51.5', 'odds': 1.72},
    {'match': 'Phoenix @ OKC', 'stage': 'Q1', 'market': 'Over 53.5', 'odds': 1.68}
]

football_feed = [
    {'match': 'AS FAR vs RS Berkane', 'league': 'Botola Pro', 'market': 'Under 2.5', 'odds': 1.62},
    {'match': 'Man City @ Burnley', 'league': 'Premier League', 'market': 'City Over 1.5', 'odds': 1.60}
]

# --- 4. DISPLAY WITH INDIVIDUAL BETTING BARS ---
tab1, tab2 = st.tabs(["🏀 NBA Quarters", "⚽ Elite Football"])

def display_betting_bar(game_name, market, odds):
    """Generates the individual betting action bar for each game."""
    stake, payout = engine.calculate_results(odds)
    
    with st.container():
        # High-visibility Betting Bar
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        
        with col1:
            st.markdown(f"**{game_name}**")
            st.caption(f"Target: {market}")
        
        with col2:
            st.metric("Odds", f"{odds}")
        
        with col3:
            if isinstance(stake, float):
                st.metric("Bet Stake", f"${stake}")
            else:
                st.error(stake)
        
        with col4:
            if isinstance(payout, float):
                st.metric("Potential Payout", f"${payout}")
                next_loss = acc_loss + stake
                st.warning(f"If Loss: Apply ${next_loss} to next event")
        st.markdown("---")

with tab1:
    st.subheader("NBA Live Signals")
    for game in nba_feed:
        display_betting_bar(game['match'], f"{game['stage']} {game['market']}", game['odds'])

with tab2:
    st.subheader("Elite Football Signals")
    for match in football_feed:
        display_betting_bar(match['match'], f"{match['league']} {match['market']}", match['odds'])

# HISTORY LOG
st.subheader("📜 Cycle History")
if 'log' not in st.session_state: st.session_state.log = []
c1, c2 = st.columns(2)
if c1.button("✅ WIN: Reset Cycle"):
    st.session_state.log.append("WIN: Cycle Reset")
    st.balloons()
if c2.button("❌ LOSS: Proceed to Martingale"):
    st.session_state.log.append(f"LOSS: Carry ${acc_loss} forward")
st.write(st.session_state.log)
