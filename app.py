import streamlit as st
import pandas as pd
import requests
import math

# --- 1. SETTINGS ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576'
BASE_BET = 100.0
STD_DEV = 4.2
DEFAULT_AVG = 28.5

TEAM_STATS = {
    "Atlanta Hawks": 30.1, "Boston Celtics": 28.7, "Brooklyn Nets": 26.5,
    "Charlotte Hornets": 27.2, "Chicago Bulls": 28.1, "Cleveland Cavaliers": 29.8,
    "Dallas Mavericks": 29.5, "Denver Nuggets": 30.5, "Detroit Pistons": 29.4,
    "Golden State Warriors": 28.6, "Houston Rockets": 28.3, "Indiana Pacers": 31.2,
    "LA Clippers": 28.4, "Los Angeles Lakers": 29.9, "Memphis Grizzlies": 27.8,
    "Miami Heat": 30.2, "Milwaukee Bucks": 27.6, "Minnesota Timberwolves": 28.2,
    "New Orleans Pelicans": 28.5, "New York Knicks": 29.1, "Oklahoma City Thunder": 29.7,
    "Orlando Magic": 26.9, "Philadelphia 76ers": 28.8, "Phoenix Suns": 29.2,
    "Portland Trail Blazers": 27.1, "Sacramento Kings": 27.7, "San Antonio Spurs": 29.9,
    "Toronto Raptors": 28.0, "Utah Jazz": 28.9, "Washington Wizards": 30.4
}

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=300) # Cache for 5 mins to save API credits
def fetch_daily_signals():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    try:
        res = requests.get(url)
        data = res.json()
        if not isinstance(data, list): return []
        
        leads = []
        for game in data:
            home, away = game.get('home_team'), game.get('away_team')
            avg = (TEAM_STATS.get(home, DEFAULT_AVG) + TEAM_STATS.get(away, DEFAULT_AVG)) / 2
            
            bookies = game.get('bookmakers', [])
            if not bookies: continue
            
            for m in bookies[0].get('markets', []):
                if m['key'] == 'totals':
                    line = m['outcomes'][0]['point'] / 4 
                    z = (line - avg) / STD_DEV
                    prob = 0.5 * (1 + math.erf(-z / math.sqrt(2)))
                    
                    leads.append({
                        "Matchup": f"{home} vs {away}",
                        "Instruction": f"OVER {line}",
                        "Prob": round(prob * 100, 1),
                        "Edge": round(avg - line, 2)
                    })
        return leads
    except: return []

# --- 3. PERSISTENT STATE ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'game_index' not in st.session_state: st.session_state.game_index = 0

# --- 4. UI TERMINAL ---
st.set_page_config(page_title="Sovereign Execution", layout="centered")
st.title("🤖 Sovereign: Step-By-Step")

leads = fetch_daily_signals()

if leads:
    # Handle index out of bounds
    if st.session_state.game_index >= len(leads):
        st.session_state.game_index = 0
        
    current_game = leads[st.session_state.game_index]
    stake = BASE_BET * (2 ** st.session_state.step)

    # Main Display Card
    st.markdown(f"""
        <div style="border: 2px solid #58a6ff; padding: 20px; border-radius: 15px; background-color: #0d1117;">
            <h4 style="color: #8b949e; margin-bottom: 5px;">ACTIVE SIGNAL {st.session_state.game_index + 1} OF {len(leads)}</h4>
            <h1 style="color: white; margin-top: 0;">{current_game['Matchup']}</h1>
            <hr style="border: 0.5px solid #30363d;">
            <div style="display: flex; justify-content: space-between;">
                <div><p style="color: #8b949e;">TARGET</p><h2 style="color: #3fb950;">{current_game['Instruction']}</h2></div>
                <div><p style="color: #8b949e;">PROBABILITY</p><h2>{current_game['Prob']}%</h2></div>
                <div><p style="color: #8b949e;">STAKE</p><h2>${stake}</h2></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write("")
    
    # Control Row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ WIN", use_container_width=True):
            st.session_state.step = 0
            st.session_state.game_index += 1
            st.balloons()
            st.rerun()
            
    with col2:
        if st.button("❌ LOSS", use_container_width=True):
            st.session_state.step += 1
            st.session_state.game_index += 1
            st.rerun()
            
    with col3:
        if st.button("➡️ SKIP", use_container_width=True):
            st.session_state.game_index += 1
            st.rerun()

    st.caption(f"Current Recovery Step: {st.session_state.step} | Total Daily Leads: {len(leads)}")

else:
    st.warning("No active signals found. Markets may be closed or refreshing.")
    if st.button("🔄 Reload Markets"): st.rerun()
