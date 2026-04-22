import streamlit as st
import pandas as pd
import requests
import math

# --- 1. CONFIG ---
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

# --- 2. ENGINE ---
@st.cache_data(ttl=600)
def get_all_daily_leads():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    try:
        data = requests.get(url).json()
        if not isinstance(data, list): return pd.DataFrame()
        
        rows = []
        for game in data:
            home, away = game.get('home_team'), game.get('away_team')
            avg = (TEAM_STATS.get(home, DEFAULT_AVG) + TEAM_STATS.get(away, DEFAULT_AVG)) / 2
            
            bookies = game.get('bookmakers', [])
            if bookies:
                for m in bookies[0].get('markets', []):
                    if m['key'] == 'totals':
                        line = m['outcomes'][0]['point'] / 4 
                        z = (line - avg) / STD_DEV
                        prob = 0.5 * (1 + math.erf(-z / math.sqrt(2)))
                        rows.append({
                            "Matchup": f"{home} vs {away}",
                            "Line": line,
                            "Prob": round(prob * 100, 1),
                            "Edge": round(avg - line, 2)
                        })
        return pd.DataFrame(rows).sort_values(by="Prob", ascending=False)
    except: return pd.DataFrame()

# --- 3. SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 4. UI ---
st.set_page_config(page_title="Sovereign Command", layout="wide")
st.title("🤖 Sovereign Command Center")

df = get_all_daily_leads()

col_table, col_terminal = st.columns([1, 1])

with col_table:
    st.subheader("📅 Daily Smart Table")
    st.write("Select a game to load into the terminal:")
    
    # Selection logic using a dataframe with a button
    if not df.empty:
        # We display the table and use a selectbox to 'pick' the game one by one
        game_list = df['Matchup'].tolist()
        choice = st.selectbox("Pick a Target Matchup:", game_list)
        
        if choice:
            st.session_state.selected_game = df[df['Matchup'] == choice].iloc[0]
            
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No active lines found. Ensure API key is active.")

with col_terminal:
    st.subheader("⚡ Execution Terminal")
    
    if st.session_state.selected_game is not None:
        g = st.session_state.selected_game
        stake = BASE_BET * (2 ** st.session_state.step)
        
        st.markdown(f"""
            <div style="background-color:#161b22; padding:30px; border-radius:15px; border:2px solid #3fb950;">
                <h2 style="margin:0; color:#8b949e;">ACTIVE TARGET</h2>
                <h1 style="margin:10px 0;">{g['Matchup']}</h1>
                <hr>
                <div style="display:flex; justify-content:space-between;">
                    <div><p>INSTRUCTION</p><h3>OVER {g['Line']}</h3></div>
                    <div><p>PROBABILITY</p><h3>{g['Prob']}%</h3></div>
                    <div><p>STAKE</p><h3 style="color:#3fb950;">${stake}</h3></div>
                </div>
                <p style="color:#8b949e; font-size: 0.8em; margin-top:20px;">RECOVERY STEP: {st.session_state.step + 1}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        c1, c2 = st.columns(2)
        if c1.button("✅ SIGNAL WON (RESET)", use_container_width=True):
            st.session_state.step = 0
            st.balloons()
            st.rerun()
        if c2.button("❌ SIGNAL LOST (DOUBLE)", use_container_width=True):
            st.session_state.step += 1
            st.rerun()
    else:
        st.write("Select a game from the table on the left to begin.")

st.caption("Engine: Dynamic Matchup Mean + Martingale Recovery Protocol")
