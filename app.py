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

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=600)
def get_all_daily_leads():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    try:
        res = requests.get(url)
        data = res.json()
        
        if isinstance(data, dict): # Check for API errors
            return pd.DataFrame()
        
        rows = []
        for game in data:
            home = game.get('home_team')
            away = game.get('away_team')
            avg = (TEAM_STATS.get(home, DEFAULT_AVG) + TEAM_STATS.get(away, DEFAULT_AVG)) / 2
            
            bookies = game.get('bookmakers', [])
            if bookies:
                for m in bookies[0].get('markets', []):
                    if m['key'] == 'totals':
                        outcome = m['outcomes'][0]
                        # Capture all necessary data for the terminal
                        rows.append({
                            "Matchup": f"{home} vs {away}",
                            "Line": round(outcome['point'] / 4, 1),
                            "Odds": outcome.get('price', 1.91),
                            "Prob": round((0.5 * (1 + math.erf(-( (outcome['point']/4) - avg) / math.sqrt(2) / STD_DEV))) * 100, 1)
                        })
        return pd.DataFrame(rows).sort_values(by="Prob", ascending=False)
    except:
        return pd.DataFrame()

# --- 3. SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 4. UI ---
st.set_page_config(page_title="Sovereign Command", layout="wide")
st.title("🤖 Sovereign Command")

df = get_all_daily_leads()

col_table, col_terminal = st.columns([1, 1.2])

with col_table:
    st.subheader("📅 Daily Smart Table")
    if not df.empty:
        # Use index-based selection to keep the 'g' object healthy
        game_list = df['Matchup'].tolist()
        choice = st.selectbox("Select Target Matchup:", ["-- Select a Game --"] + game_list)
        
        if choice != "-- Select a Game --":
            st.session_state.selected_game = df[df['Matchup'] == choice].iloc[0].to_dict()
            
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Searching for lines...")

with col_terminal:
    st.subheader("⚡ Execution Terminal")
    
    g = st.session_state.selected_game
    # CRITICAL: Only run if 'Odds' key exists to prevent KeyError
    if g and 'Odds' in g:
        stake = BASE_BET * (2 ** st.session_state.step)
        net_profit = (stake * g['Odds']) - stake
        
        st.markdown(f"""
            <div style="background-color:#0d1117; padding:30px; border-radius:15px; border:2px solid #58a6ff;">
                <h1 style="margin:0 0 10px 0; color:white;">{g['Matchup']}</h1>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid #30363d; padding-bottom:15px;">
                    <div><p style="color:#8b949e; margin:0;">INSTRUCTION</p><h2 style="color:#3fb950; margin:0;">OVER {g['Line']}</h2></div>
                    <div><p style="color:#8b949e; margin:0;">ODDS</p><h2 style="margin:0;">{g['Odds']}</h2></div>
                    <div><p style="color:#8b949e; margin:0;">STAKE</p><h2 style="margin:0;">${stake}</h2></div>
                </div>
                <div style="margin-top:20px;">
                    <p style="color:#8b949e; margin:0;">POTENTIAL PROFIT</p>
                    <h1 style="color:#3fb950; margin:0;">+ ${net_profit:,.2f}</h1>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        c1, c2 = st.columns(2)
        if c1.button("✅ WIN (RESET)"):
            st.session_state.step = 0
            st.rerun()
        if c2.button("❌ LOSS (DOUBLE)"):
            st.session_state.step += 1
            st.rerun()
    else:
        st.write("Target selection required to initialize terminal.")

st.caption(f"Recovery Step: {st.session_state.step + 1} | Base Stake: ${BASE_BET}")
