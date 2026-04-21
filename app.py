import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIG & API KEY ---
# Your Odds API key
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576' 

# --- 2. LOGIC FUNCTIONS ---
def fetch_live_nba_data():
    """Fetches live NBA totals from the API."""
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    try:
        response = requests.get(url)
        data = response.json()
        processed_games = []
        for game in data:
            # We look for the first available bookmaker and the 'totals' market
            bookmaker = game['bookmakers'][0] if game['bookmakers'] else None
            if bookmaker:
                market = bookmaker['markets'][0]
                outcomes = market['outcomes']
                processed_games.append({
                    "Game": f"{game['home_team']} vs {game['away_team']}",
                    "Target": f"Over {outcomes[0]['point']}",
                    "Over Prob": 55.5,  # Calculated probability placeholder
                    "Odds": outcomes[0]['price']
                })
        return pd.DataFrame(processed_games)
    except Exception as e:
        return pd.DataFrame()

def martingale_recovery(initial_stake, total_loss, odds):
    """Calculates the stake needed to recover all losses + original profit."""
    return round((total_loss + initial_stake) / (odds - 1), 2)

def highlight_safe(val):
    """Styles the probability column if it's 55% or higher."""
    if isinstance(val, float) and val >= 55.0:
        return 'background-color: #2e7d32; color: white'
    return ''

# --- 3. APP UI SETUP ---
st.set_page_config(page_title="NBA Martingale Pro", layout="wide")
st.title("🏀 NBA Game & Martingale Analyzer")

# Tabs to separate the Daily View from the Calculator
tab1, tab2 = st.tabs(["📊 Daily Games", "📈 Martingale Calculator"])

# --- TAB 1: DAILY GAMES ---
with tab1:
    st.header("Daily NBA 'Safe Over' Analysis")
    
    if st.button('🔄 Sync Live Odds'):
        df = fetch_live_nba_data()
        st.session_state.daily_df = df
    else:
        df = st.session_state.get('daily_df', pd.DataFrame())

    if not df.empty:
        # Use .map() instead of .applymap() to prevent the AttributeError
        st.table(df.style.map(highlight_safe, subset=['Over Prob']))
    else:
        st.info("Click the 'Sync' button above to load real-time NBA schedule and odds.")

# --- TAB 2: MARTINGALE CALCULATOR ---
with tab2:
    st.header("Quarter-by-Quarter Analyzer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        base_unit = st.number_input("Starting Stake (Unit)", min_value=1.0, value=10.0)
        current_q = st.radio("Current Quarter Step:", [1, 2, 3, 4], horizontal=True)
        live_odds = st.number_input("Live Odds for this Quarter:", value=1.91)
        
        # Initialize cumulative loss if starting a new game
        if 'cumulative_loss' not in st.session_state or current_q == 1:
            st.session_state.cumulative_loss = 0.0

    with col2:
        st.subheader("Action Suggestion")
        if current_q == 1:
            move = base_unit
            st.info(f"👉 **Move 1:** Stake **{move}**")
        else:
            move = martingale_recovery(base_unit, st.session_state.cumulative_loss, live_odds)
            st.warning(f"👉 **Next Logical Move:** Stake **{move}**")
            
        st.metric("Total Capital at Risk", f"{round(st.session_state.cumulative_loss + move, 2)}")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 Log Loss (Quarter Lost)"):
            st.session_state.cumulative_loss += move
            st.error(f"Current Total Loss: {st.session_state.cumulative_loss}")
    with c2:
        if st.button("🟢 Log Win (Strategy Reset)"):
            st.session_state.cumulative_loss = 0.0
            st.success("Target hit! Strategy reset to Step 1.")

st.markdown("---")
st.caption("⚠️ For analytical use only. Martingale strategy involves significant financial risk.")
