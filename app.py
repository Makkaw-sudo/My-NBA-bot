import streamlit as st
import pandas as pd
import requests
import math
import numpy as np
from scipy.stats import poisson

# --- 1. SETTINGS ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576'
BASE_BET = 100.0
NBA_STD_DEV = 4.2
DEFAULT_AVG = 28.5

# Standard averages for NBA teams (Points per Quarter)
NBA_STATS = {
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

# --- 2. DATA ENGINES ---
@st.cache_data(ttl=600)
def get_nba_data():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    try:
        data = requests.get(url).json()
        rows = []
        for game in data:
            home, away = game.get('home_team'), game.get('away_team')
            avg = (NBA_STATS.get(home, DEFAULT_AVG) + NBA_STATS.get(away, DEFAULT_AVG)) / 2
            bookies = game.get('bookmakers', [])
            if bookies:
                for m in bookies[0].get('markets', []):
                    if m['key'] == 'totals':
                        outcome = m['outcomes'][0]
                        line = outcome['point'] / 4
                        odds = outcome['price']
                        z = (line - avg) / NBA_STD_DEV
                        prob = 0.5 * (1 + math.erf(-z / math.sqrt(2)))
                        rows.append({"Matchup": f"{home} vs {away}", "Line": round(line, 1), "Odds": odds, "Prob": round(prob * 100, 1)})
        return pd.DataFrame(rows).sort_values(by="Prob", ascending=False)
    except: return pd.DataFrame()

# --- 3. UI GENERATOR ---
def main():
    st.set_page_config(page_title="Sovereign Intelligence", layout="wide")
    
    if 'step' not in st.session_state: st.session_state.step = 0
    if 'selected_game' not in st.session_state: st.session_state.selected_game = None

    st.sidebar.title("🎮 Command Switch")
    mode = st.sidebar.radio("Active Engine:", ["NBA Basketball", "Soccer Football"])
    st.sidebar.divider()
    st.sidebar.metric("Current Martingale Step", st.session_state.step + 1)
    if st.sidebar.button("Reset Sequence"): 
        st.session_state.step = 0
        st.rerun()

    if mode == "NBA Basketball":
        st.title("🏀 NBA Intelligence Terminal")
        df = get_nba_data()
        
        col_list, col_brief = st.columns([1, 1.3])
        
        with col_list:
            st.subheader("📅 Today's Opportunities")
            if not df.empty:
                game_list = df['Matchup'].tolist()
                choice = st.selectbox("Select a game to analyze:", ["-- Pick Game --"] + game_list)
                if choice != "-- Pick Game --":
                    st.session_state.selected_game = df[df['Matchup'] == choice].iloc[0].to_dict()
                st.dataframe(df, use_container_width=True, hide_index=True)
            else: st.info("No games found. Check API Key.")

        with col_brief:
            st.subheader("⚡ Strategy Briefing")
            g = st.session_state.selected_game
            if g:
                stake = BASE_BET * (2 ** st.session_state.step)
                profit = (stake * g['Odds']) - stake
                edge = round(g['Prob'] - (100 / g['Odds']), 2)

                st.markdown(f"""
                <div style="background:#0d1117; padding:25px; border-radius:15px; border:2px solid #58a6ff;">
                    <h1 style="color:white; margin:0;">{g['Matchup']}</h1>
                    <h2 style="color:#3fb950; margin:10px 0;">INSTRUCTION: BET ${stake} ON OVER {g['Line']}</h2>
                    <hr style="border-color:#30363d">
                    <h4 style="color:#f1e05a;">🎯 WHY? (THE REASONING)</h4>
                    <p style="color:#8b949e;">The market has priced this line at <b>{g['Line']}</b>. Our model shows a <b>{g['Prob']}%</b> probability of exceeding this. You have a <b>{edge}% mathematical edge</b> over the bookmaker.</p>
                    <h4 style="color:#f1e05a;">📊 WHAT'S HAPPENING?</h4>
                    <p style="color:#8b949e;">By placing this bet, you are exploiting an outlier. If successful, you profit <b>${profit:,.2f}</b>. If not, the Martingale system will trigger a recovery stake of <b>${stake * 2}</b> for the next event.</p>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                if c1.button("✅ SIGNAL WON (RESET)"):
                    st.session_state.step = 0
                    st.balloons()
                    st.rerun()
                if c2.button("❌ SIGNAL LOST (RECOVER)"):
                    st.session_state.step += 1
                    st.rerun()
            else: st.warning("Please select a game from the list to see the strategy.")

    else:
        st.title("⚽ Soccer Poisson Engine")
        st.write("Manual calculation mode for Soccer value detection.")
        # Soccer logic follows here...
        bankroll = st.sidebar.number_input("Bankroll ($)", value=5000.0)
        h_exp = st.number_input("Home Expected Goals", value=1.5)
        a_exp = st.number_input("Away Expected Goals", value=1.2)
        odds = st.number_input("Bookie Odds (Home Win)", value=2.0)
        
        # Poisson Math
        p_home = np.sum(np.tril(np.outer([poisson.pmf(i, h_exp) for i in range(10)], [poisson.pmf(i, a_exp) for i in range(10)]), -1))
        
        if p_home > (1/odds):
            st.success(f"VALUE DETECTED: {round(p_home*100, 1)}% Prob. Bet recommended.")
        else: st.error("NO EDGE. SKIP EVENT.")

if __name__ == "__main__":
    main()
