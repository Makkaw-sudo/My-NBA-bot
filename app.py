import streamlit as st
import pandas as pd
import requests

API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576' 

def fetch_live_nba_data():
    # Looking for both Game Totals and Q1 Totals
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals,totals_q1&oddsFormat=decimal"
    try:
        response = requests.get(url)
        data = response.json()
        processed_games = []
        for game in data:
            bookmaker = game['bookmakers'][0] if game['bookmakers'] else None
            if bookmaker:
                # Check if Q1 odds exist; if not, use full game
                q1 = next((m for m in bookmaker['markets'] if m['key'] == 'totals_q1'), None)
                m = q1 if q1 else bookmaker['markets'][0]
                label = "Q1 Over" if q1 else "Game Over"
                
                processed_games.append({
                    "Game": f"{game['home_team']} vs {game['away_team']}",
                    "Target": f"{label} {m['outcomes'][0]['point']}",
                    "Over Prob": 55.5, 
                    "Odds": m['outcomes'][0]['price']
                })
        return pd.DataFrame(processed_games)
    except:
        return pd.DataFrame()

# --- Simple UI ---
st.title("🏀 NBA Quarter Tracker")

if st.button('🔄 Sync Quarters'):
    df = fetch_live_nba_data()
    if not df.empty:
        st.table(df)
    else:
        st.warning("No Quarter lines found yet. Check back closer to tip-off!")
