import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIG & API KEY ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576' 

# --- 2. LOGIC FUNCTIONS ---
def fetch_live_nba_data():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    try:
        response = requests.get(url)
        data = response.json()
        processed_games = []
        for game in data:
            bookmaker = game['bookmakers'][0] if game['bookmakers'] else None
            if bookmaker:
                market = bookmaker['markets'][0]
                outcomes = market['outcomes']
                processed_games.append({
                    "Game": f"{game['home_team']} vs {game['away_team']}",
                    "Target": f"Over {outcomes[0]['point']}",
                    "Over Prob": 55.5, 
                    "Odds": outcomes[0]['price']
                })
        return pd.DataFrame(processed_games)
    except Exception as e:
        return pd.DataFrame()

def martingale_recovery(initial_stake, total_loss, odds):
    return round((total_loss + initial_stake) / (odds - 1), 2)

def highlight_safe(val):
    if isinstance(val, float) and val >= 55.0:
        return 'background-color: #2e7d32; color: white'
    return ''

# --- 3. APP UI ---
st.set_page_config(page_title="NBA Martingale Pro", layout="wide")
st.title("🏀 NBA Game & Martingale Analyzer")

tab1, tab2 = st.tabs(["📊 Daily Games", "📈 Martingale Calculator"])

with tab1:
    st.header("Daily NBA Analysis")
    if st.button('🔄 Sync Live Odds'):
        df = fetch_live_nba_data()
        st.session_state.daily_df = df
    else:
        df = st.session_state.get('daily_df', pd.DataFrame())

    if not df.empty:
        # This line is the fix! .map instead of .applymap
        st.table(df.style.map(highlight_safe, subset=['Over Prob']))
    else:
        st.info("Click 'Sync' to load data.")

with tab2:
    st.header("Martingale Calculator")
    base_unit = st.number_input("Starting Stake", min_value=1.0, value=10.0)
    current_q = st.radio("Quarter:", [1, 2, 3, 4], horizontal=True)
    live_odds = st.number_input("Odds:", value=1.91)
    
    if 'cumulative_loss' not in st.session_state or current_q == 1:
        st.session_state.cumulative_loss = 0.0

    if current_q == 1:
        move = base_unit
    else:
        move = martingale_recovery(base_unit, st.session_state.cumulative_loss, live_odds)

    st.metric("Suggested Move", f"{move}")
    
    if st.button("🔴 Log Loss"):
        st.session_state.cumulative_loss += move
    if st.button("🟢 Log Win"):
        st.session_state.cumulative_loss = 0.0
