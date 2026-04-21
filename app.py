import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone
import math

# --- 1. CONFIG ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576' 

# --- 2. STYLING ---
st.set_page_config(page_title="NBA Elite Terminal", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    .countdown-box { 
        padding: 10px; border-radius: 8px; text-align: center; 
        font-weight: bold; border: 1px solid #30363d;
    }
    .urgent { background-color: #7e1d1d; color: white; border: 1px solid #f85149; }
    .ready { background-color: #238636; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOGIC WITH COUNTDOWN ---
def fetch_timed_data(market_key):
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets={market_key}&oddsFormat=decimal"
    try:
        response = requests.get(url)
        data = response.json()
        processed = []
        now = datetime.now(timezone.utc)
        
        for game in data:
            # Parse start time
            start_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            time_diff = start_time - now
            minutes_left = int(time_diff.total_seconds() / 60)
            
            bookie = game['bookmakers'][0] if game['bookmakers'] else None
            if bookie:
                m = bookie['markets'][0]
                # Detail logic: More info if close to start
                status = "🚨 URGENT" if 0 < minutes_left < 30 else "⏳ WAITING"
                if minutes_left < 0: status = "🏀 LIVE"

                processed.append({
                    "STATUS": status,
                    "START IN": f"{minutes_left} min" if minutes_left > 0 else "LIVE",
                    "MATCHUP": f"{game['home_team']} vs {game['away_team']}",
                    "LINE": f"O {m['outcomes'][0]['point']}",
                    "BEST ODDS": m['outcomes'][0]['price'],
                    "RAW_MINS": minutes_left # Hidden for sorting
                })
        
        df = pd.DataFrame(processed)
        if not df.empty:
            return df.sort_values(by="RAW_MINS") # Closest games at the top
        return df
    except:
        return pd.DataFrame()

# --- 4. INTERFACE ---
st.title("🛡️ NBA Elite: Precision Terminal")

if 'pnl' not in st.session_state: st.session_state.pnl = 0.0

# Dashboard Header
h1, h2, h3 = st.columns([1, 1, 1])
h1.metric("Session P/L", f"${st.session_state.pnl}")
h2.write(f"**Current Time (UTC):** {datetime.now(timezone.utc).strftime('%H:%M')}")
if h3.button("🔄 REFRESH ALL DATA"):
    st.session_state.df = fetch_timed_data("totals,totals_q1")

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("🕒 Live Tip-off Countdown")
    df = st.session_state.get('df', pd.DataFrame())
    
    if not df.empty:
        # Style the dataframe based on urgency
        def color_status(val):
            if "🚨" in val: return 'color: #f85149; font-weight: bold'
            if "🏀" in val: return 'color: #3fb950; font-weight: bold'
            return 'color: #8b949e'

        st.dataframe(
            df.drop(columns=['RAW_MINS']).style.applymap(color_status, subset=['STATUS']),
            use_container_width=True,
            hide_index=True
        )
        
        # Automatic Insight
        urgent_games = df[df['STATUS'] == "🚨 URGENT"]
        if not urgent_games.empty:
            st.warning(f"**Action Required:** {len(urgent_games)} games starting in less than 30 mins. Lock in your Q1 units.")
    else:
        st.info("Tap Refresh to scan for upcoming NBA tip-offs.")

with right:
    st.subheader("⚡ Martingale Engine")
    with st.form("martingale_form"):
        unit = st.number_input("Target Profit", value=10.0)
        lost = st.number_input("Total Lost", value=0.0)
        odds = st.number_input("Current Odds", value=1.91)
        
        stake = round((lost + unit) / (odds - 1), 2)
        
        st.markdown(f"### Next Stake")
        st.markdown(f"<h1 style='color: #58a6ff;'>${stake}</h1>", unsafe_allow_html=True)
        
        if st.form_submit_button("💰 LOG WIN"):
            st.session_state.pnl += unit
            st.balloons()
            st.rerun()

st.caption("v3.5 Precision Timing | Automated Tip-off Detection")
