import streamlit as st
import pandas as pd
import requests
import math
import numpy as np
from scipy.stats import poisson

# --- 1. GLOBAL CONFIG ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576'
BASE_BET = 100.0
NBA_STD_DEV = 4.2
DEFAULT_AVG = 28.5

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

# --- 2. NBA ENGINE ---
@st.cache_data(ttl=600)
def get_nba_leads():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    try:
        data = requests.get(url).json()
        if not isinstance(data, list): return pd.DataFrame()
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
                        rows.append({
                            "Matchup": f"{home} vs {away}",
                            "Line": round(line, 1),
                            "Odds": odds,
                            "Prob": round(prob * 100, 1)
                        })
        return pd.DataFrame(rows).sort_values(by="Prob", ascending=False)
    except: return pd.DataFrame()

def run_nba_mode():
    st.header("🏀 NBA Execution Terminal")
    df = get_nba_leads()
    col_t, col_e = st.columns([1, 1.2])
    
    with col_t:
        st.subheader("Daily Smart Table")
        if not df.empty:
            game_list = df['Matchup'].tolist()
            choice = st.selectbox("Load Matchup:", ["-- Select --"] + game_list)
            if choice != "-- Select --":
                st.session_state.selected_game = df[df['Matchup'] == choice].iloc[0].to_dict()
            st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("No active lines.")

    with col_e:
        st.subheader("Terminal")
        g = st.session_state.selected_game
        if g and 'Odds' in g:
            stake = BASE_BET * (2 ** st.session_state.step)
            net_profit = (stake * g['Odds']) - stake
            st.markdown(f"""
                <div style="background:#0d1117; padding:20px; border-radius:15px; border:2px solid #58a6ff;">
                    <h2 style="margin:0;">{g['Matchup']}</h2>
                    <hr>
                    <div style="display:flex; justify-content:space-between;">
                        <div><p>TARGET</p><h3>OVER {g['Line']}</h3></div>
                        <div><p>ODDS</p><h3>{g['Odds']}</h3></div>
                        <div><p>STAKE</p><h3>${stake}</h3></div>
                    </div>
                    <h2 style="color:#3fb950; margin-top:15px;">Profit: +${net_profit:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)
            st.write("")
            c1, c2 = st.columns(2)
            if c1.button("✅ WIN", use_container_width=True):
                st.session_state.step = 0
                st.balloons()
                st.rerun()
            if c2.button("❌ LOSS", use_container_width=True):
                st.session_state.step += 1
                st.rerun()
        else: st.warning("Pick a game to initialize.")

# --- 3. SOCCER ENGINE ---
def run_soccer_mode():
    st.header("⚽ Soccer Poisson Terminal")
    st.write("Calculate true probability and optimal stake using the Kelly Criterion.")
    
    with st.container():
        c1, c2, c3 = st.columns(3)
        h_exp = c1.number_input("Home Exp Goals (λ)", value=1.5, step=0.1)
        a_exp = c2.number_input("Away Exp Goals (λ)", value=1.2, step=0.1)
        m_odds = c3.number_input("Market Odds (Home Win)", value=2.0)
        
        bankroll = st.sidebar.number_input("Total Bankroll ($)", value=1000.0)

        # Poisson Math
        max_g = 10
        h_p = [poisson.pmf(i, h_exp) for i in range(max_g)]
        a_p = [poisson.pmf(i, a_exp) for i in range(max_g)]
        matrix = np.outer(h_p, a_p)
        p_home = np.sum(np.tril(matrix, -1))
        
        edge = p_home - (1/m_odds)
        
        # Kelly Criterion
        b = m_odds - 1
        f_star = (b * p_home - (1-p_home)) / b
        safe_stake = max(0, f_star * bankroll * 0.25) # Quarter Kelly

        st.divider()
        res1, res2 = st.columns(2)
        res1.metric("Home Win Prob", f"{round(p_home*100, 1)}%")
        res1.metric("Mathematical Edge", f"{round(edge*100, 2)}%")
        
        if edge > 0:
            res2.success(f"✅ VALUE DETECTED")
            res2.metric("RECOMENDED STAKE", f"${round(safe_stake, 2)}")
            st.caption("Stake calculated using Quarter-Kelly to prevent loss of bankroll.")
        else:
            res2.error("❌ NO VALUE")

# --- 4. MAIN ROUTER ---
def main():
    st.set_page_config(page_title="Sovereign Multi-Sport", layout="wide")
    
    if 'step' not in st.session_state: st.session_state.step = 0
    if 'selected_game' not in st.session_state: st.session_state.selected_game = None

    st.sidebar.title("🎮 Sovereign Controller")
    mode = st.sidebar.radio("Switch Engine:", ["NBA Basketball", "Soccer Football"])
    
    st.sidebar.divider()
    st.sidebar.write(f"**Martingale Step:** {st.session_state.step + 1}")
    if st.sidebar.button("Reset Martingale"):
        st.session_state.step = 0
        st.rerun()

    if mode == "NBA Basketball":
        run_nba_mode()
    else:
        run_soccer_mode()

if __name__ == "__main__":
    main()
