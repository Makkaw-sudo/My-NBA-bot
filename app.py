import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIG ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576' 

def fetch_nba_data(market_key):
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets={market_key}&oddsFormat=decimal"
    try:
        response = requests.get(url)
        data = response.json()
        processed = []
        for game in data:
            bookie = game['bookmakers'][0] if game['bookmakers'] else None
            if bookie:
                m = bookie['markets'][0]
                processed.append({
                    "Matchup": f"{game['home_team']} vs {game['away_team']}",
                    "Line": f"{m['outcomes'][0]['point']}",
                    "Odds": m['outcomes'][0]['price']
                })
        return pd.DataFrame(processed)
    except:
        return pd.DataFrame()

# --- 2. APP UI & STYLE ---
st.set_page_config(page_title="NBA Martingale Pro", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for "Fancy" buttons
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #007bff;
        color: white;
        height: 3em;
        width: 100%;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #0056b3;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏀 NBA Martingale Terminal")

# --- 3. FANCY HOME SCREEN BUTTONS (COMMAND CENTER) ---
st.subheader("⚡ Quick Sync Commands")
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🏟️ FULL GAME"):
        st.session_state.live_df = fetch_nba_data("totals")
        st.session_state.current_market = "Full Game"
with c2:
    if st.button("1️⃣ QUARTER 1"):
        st.session_state.live_df = fetch_nba_data("totals_q1")
        st.session_state.current_market = "Q1"
with c3:
    if st.button("2️⃣ QUARTER 2"):
        st.session_state.live_df = fetch_nba_data("totals_q2")
        st.session_state.current_market = "Q2"
with c4:
    if st.button("➕ MORE QUARTERS"):
        st.session_state.live_df = fetch_nba_data("totals_q3,totals_q4")
        st.session_state.current_market = "Late Quarters"

st.divider()

# --- 4. MAIN CONTENT AREA ---
left, right = st.columns([2, 1])

with left:
    market_label = st.session_state.get('current_market', 'Select a Market')
    st.subheader(f"📡 Live Feed: {market_label}")
    
    df = st.session_state.get('live_df', pd.DataFrame())
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Tap a button above to pull live NBA lines.")

with right:
    st.subheader("📈 Recovery Tools")
    
    # Simple Bankroll Metric
    if 'profit' not in st.session_state: st.session_state.profit = 0.0
    st.metric("Session P/L", f"${st.session_state.profit}", delta=st.session_state.profit if st.session_state.profit != 0 else None)
    
    with st.expander("🧮 Martingale Calculator", expanded=True):
        unit = st.number_input("Base Stake ($)", value=10.0)
        loss = st.number_input("Total Loss ($)", value=0.0)
        odds = st.number_input("Next Odds", value=1.91)
        
        recovery = round((loss + unit) / (odds - 1), 2)
        st.markdown(f"### Next Stake: :red[${recovery}]")
        
        if st.button("💰 LOG WIN (RESET)"):
            st.session_state.profit += unit
            st.balloons()
            st.rerun()

st.caption("🚀 Optimized for Mobile High-Speed Execution")
