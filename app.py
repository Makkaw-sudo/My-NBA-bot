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
                        outcome = m['outcomes'][0] # Usually the 'Over'
                        line = outcome['point'] / 4 
                        odds = outcome['price'] # This is the multiplier (e.g. 1.91)
                        
                        z = (line - avg) / STD_DEV
                        prob = 0.5 * (1 + math.erf(-z / math.sqrt(2)))
                        rows.append({
                            "Matchup": f"{home} vs {away}",
                            "Line": round(line, 1),
                            "Odds": odds,
                            "Prob": round(prob * 100, 1),
                            "Edge": round(avg - line, 2)
                        })
        return pd.DataFrame(rows).sort_values(by="Prob", ascending=False)
    except: return pd.DataFrame()

# --- 3. SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 4. UI ---
st.set_page_config(page_title="Sovereign Command v4", layout="wide")
st.title("🤖 Sovereign Command: Profit Optimizer")

df = get_all_daily_leads()

col_table, col_terminal = st.columns([1, 1.2])

with col_table:
    st.subheader("📅 Daily Smart Table")
    if not df.empty:
        game_list = df['Matchup'].tolist()
        choice = st.selectbox("Pick a Target Matchup:", game_list)
        if choice:
            st.session_state.selected_game = df[df['Matchup'] == choice].iloc[0]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No active lines found.")

with col_terminal:
    st.subheader("⚡ Execution Terminal")
    if st.session_state.selected_game is not None:
        g = st.session_state.selected_game
        stake = BASE_BET * (2 ** st.session_state.step)
        
        # PROFIT CALCULATION
        potential_return = stake * g['Odds']
        net_profit = potential_return - stake
        
        st.markdown(f"""
            <div style="background-color:#0d1117; padding:30px; border-radius:15px; border:2px solid #58a6ff;">
                <h2 style="margin:0; color:#8b949e;">ACTIVE TARGET</h2>
                <h1 style="margin:10px 0;">{g['Matchup']}</h1>
                <hr style="border-color:#30363d">
                <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                    <div><p style="color:#8b949e; margin:0;">TARGET</p><h3>OVER {g['Line']}</h3></div>
                    <div><p style="color:#8b949e; margin:0;">ODDS</p><h3>{g['Odds']}</h3></div>
                    <div><p style="color:#8b949e; margin:0;">STAKE</p><h3>${stake}</h3></div>
                </div>
                <div style="background-color:#161b22; padding:15px; border-radius:10px; border-left: 5px solid #3fb950;">
                    <p style="color:#8b949e; margin:0;">ESTIMATED NET PROFIT</p>
                    <h2 style="color:#3fb950; margin:0;">+ ${net_profit:,.2f}</h2>
                </div>
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
        st.write("Select a game from the table to calculate potential profit.")

st.caption(f"Strategy: Martingale Recovery | Base: ${BASE_BET} | Step: {st.session_state.step + 1}")
