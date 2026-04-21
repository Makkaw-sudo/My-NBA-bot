import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIG ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576' 

# --- 2. ELITE STYLING ---
st.set_page_config(page_title="NBA Elite Terminal", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #0b0e14; }
    .stMetric { background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #1f6feb 0%, #58a6ff 100%);
        border: none; border-radius: 8px; color: white; font-weight: bold; height: 3.5rem;
    }
    .status-box { padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ADVANCED DATA LOGIC ---
def fetch_elite_data(market_key):
    # This version pulls from multiple regions to find the best odds
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us,eu&markets={market_key}&oddsFormat=decimal"
    try:
        response = requests.get(url)
        data = response.json()
        processed = []
        for game in data:
            for bookie in game['bookmakers'][:3]: # Check top 3 bookmakers
                m = bookie['markets'][0]
                processed.append({
                    "MATCHUP": f"{game['home_team']} vs {game['away_team']}",
                    "BOOKIE": bookie['title'].upper(),
                    "LINE": f"O {m['outcomes'][0]['point']}",
                    "PRICE": m['outcomes'][0]['price']
                })
        return pd.DataFrame(processed)
    except:
        return pd.DataFrame()

# --- 4. THE TERMINAL INTERFACE ---
st.title("🛡️ NBA Elite Recovery Terminal")

# Persistent Session Data
if 'pnl' not in st.session_state: st.session_state.pnl = 0.0
if 'history' not in st.session_state: st.session_state.history = []

# Top Row: Command & Metrics
m1, m2, m3 = st.columns([1, 1, 2])
with m1:
    st.metric("Session P/L", f"${st.session_state.pnl}", delta=f"{st.session_state.pnl} Today")
with m2:
    risk_level = "LOW" if st.session_state.pnl >= 0 else "CAUTION"
    st.metric("Risk Status", risk_level)
with m3:
    c1, c2, c3 = st.columns(3)
    if c1.button("🏟️ GAME"): st.session_state.df = fetch_elite_data("totals")
    if c2.button("1️⃣ Q1"): st.session_state.df = fetch_elite_data("totals_q1")
    if c3.button("🔄 RESET"): st.session_state.pnl = 0.0; st.rerun()

st.divider()

# Main Workspace
left, right = st.columns([2, 1])

with left:
    st.subheader("📊 Market Arbitrage (Top 3 Bookies)")
    df = st.session_state.get('df', pd.DataFrame())
    if not df.empty:
        # Highlight the best (highest) odds in green
        st.dataframe(df.style.highlight_max(subset=['PRICE'], color='#238636'), 
                     use_container_width=True, hide_index=True)
    else:
        st.info("Select a command above to scan live markets.")

with right:
    st.subheader("⚡ Martingale Engine")
    
    with st.form("calc_form"):
        unit = st.number_input("Target Profit ($)", value=10.0)
        total_lost = st.number_input("Cumulative Loss ($)", value=0.0)
        current_odds = st.number_input("Best Available Odds", value=1.91)
        
        # Calculation logic
        stake = round((total_lost + unit) / (current_odds - 1), 2)
        
        # Risk color logic
        color = "green" if total_lost == 0 else "orange" if total_lost < (unit * 5) else "red"
        st.markdown(f"### Required Stake: :{color}[${stake}]")
        
        submitted = st.form_submit_button("💰 LOG PROFIT")
        if submitted:
            st.session_state.pnl += unit
            st.balloons()
            st.rerun()

st.caption("Elite Terminal v3.0 | Real-time Arbitrage Enabled")
