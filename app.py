import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta

# --- 1. CONFIG ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576' 

# --- 2. ELITE STYLING ---
st.set_page_config(page_title="NBA Command Center", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    [data-testid="stMetricValue"] { font-size: 24px; color: #58a6ff; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] { background-color: #1f6feb !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ADVANCED SCHEDULING LOGIC ---
def fetch_full_schedule():
    # Fetching odds which include the schedule for upcoming days
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    try:
        response = requests.get(url)
        data = response.json()
        processed = []
        now = datetime.now(timezone.utc)
        
        for game in data:
            start_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            time_diff = start_time - now
            
            # Formatting Countdown
            if time_diff.total_seconds() > 0:
                hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                countdown = f"{hours}h {minutes}m"
            else:
                countdown = "LIVE / FINISHED"

            bookie = game['bookmakers'][0] if game['bookmakers'] else None
            line = bookie['markets'][0]['outcomes'][0]['point'] if bookie else "N/A"
            odds = bookie['markets'][0]['outcomes'][0]['price'] if bookie else "N/A"

            processed.append({
                "DATE": start_time.strftime('%b %d'),
                "TIME (UTC)": start_time.strftime('%H:%M'),
                "MATCHUP": f"{game['home_team']} vs {game['away_team']}",
                "COUNTDOWN": countdown,
                "EST. LINE": line,
                "ODDS": odds,
                "RAW_TIME": start_time # For filtering
            })
        return pd.DataFrame(processed)
    except:
        return pd.DataFrame()

# --- 4. THE INTERFACE ---
st.title("📅 NBA Strategic Command Center")

# Session State for P/L
if 'pnl' not in st.session_state: st.session_state.pnl = 0.0

# Sidebar Calculator (Always visible for quick math)
with st.sidebar:
    st.header("🧮 Martingale Calc")
    unit = st.number_input("Target Profit", value=10.0)
    lost = st.number_input("Total Lost", value=0.0)
    odds_input = st.number_input("Live Odds", value=1.91)
    stake = round((lost + unit) / (odds_input - 1), 2)
    st.markdown(f"## Stake: :green[${stake}]")
    if st.button("💰 LOG WIN"):
        st.session_state.pnl += unit
        st.balloons()

# Main Dashboard Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Session P/L", f"${st.session_state.pnl}")
m2.metric("Today's Date", datetime.now().strftime('%d %B'))
if m3.button("🔄 REFRESH SCHEDULE"):
    st.session_state.sched_df = fetch_full_schedule()

st.divider()

# TABBED INTERFACE FOR SCHEDULE
df = st.session_state.get('sched_df', pd.DataFrame())

if not df.empty:
    tab_today, tab_tomorrow, tab_future = st.tabs(["🔥 Today", "🌅 Tomorrow", "📅 Upcoming"])
    
    today_date = datetime.now(timezone.utc).date()
    tomorrow_date = today_date + timedelta(days=1)

    with tab_today:
        today_df = df[df['RAW_TIME'].dt.date == today_date]
        if not today_df.empty:
            st.dataframe(today_df.drop(columns=['RAW_TIME']), use_container_width=True, hide_index=True)
        else:
            st.info("No more games scheduled for today.")

    with tab_tomorrow:
        tomorrow_df = df[df['RAW_TIME'].dt.date == tomorrow_date]
        if not tomorrow_df.empty:
            st.dataframe(tomorrow_df.drop(columns=['RAW_TIME']), use_container_width=True, hide_index=True)
        else:
            st.info("Schedule for tomorrow not yet released by bookmakers.")

    with tab_future:
        future_df = df[df['RAW_TIME'].dt.date > tomorrow_date]
        if not future_df.empty:
            st.dataframe(future_df.drop(columns=['RAW_TIME']), use_container_width=True, hide_index=True)
        else:
            st.info("Long-term schedule depends on market availability.")
else:
    st.warning("Tap 'Refresh Schedule' to load the NBA calendar.")

st.caption("Terminal v4.0 | Advanced Planning Mode")
