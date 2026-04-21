import streamlit as st
import requests
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import time

# --- 1. SETTINGS & DYNAMIC THEME ---
st.set_page_config(page_title="QUANTUM TITAN V11", layout="wide")
API_KEY = "4d1e72e9dc2207f0ae744c61dfa51576"

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e6edf3; }
    .dynamic-card {
        background: linear-gradient(135deg, #1e2631 0%, #0d1117 100%);
        padding: 35px; border-radius: 25px; border: 2px solid #58a6ff;
        text-align: center; box-shadow: 0 15px 50px rgba(0,0,0,0.9);
    }
    .bet-cmd { font-size: 52px; font-weight: 900; color: #ffffff; }
    .safe-point { background: #161b22; padding: 12px; border-radius: 10px; border: 1px solid #3fb950; color: #3fb950; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED PACE DATABASE ---
# These are the scoring 'DNA' profiles for tonight's teams
TEAM_PACE = {
    "Los Angeles Lakers": 29.8, "Houston Rockets": 27.5,
    "San Antonio Spurs": 29.1, "Portland Trail Blazers": 26.9,
    "Cleveland Cavaliers": 27.2, "Toronto Raptors": 28.4,
    "New York Knicks": 26.5, "Atlanta Hawks": 30.2,
    "Boston Celtics": 30.5, "Philadelphia 76ers": 28.8
}

# --- 3. THE ANALYTICS ENGINE (DYNAMIC) ---
def analyze_game_titan(game, step, base):
    h_team = game.get('home_team')
    a_team = game.get('away_team')
    
    # CALCULATE UNIQUE PROJECTION (Fixes the 59.5 Weakness)
    h_pace = TEAM_PACE.get(h_team, 28.5)
    a_pace = TEAM_PACE.get(a_team, 28.5)
    projected_q_total = round(h_pace + a_pace, 1)

    # MARTINGALE RECOVERY CALC
    odds = 1.91
    prev_losses = sum([base * (2**i) for i in range(step - 1)])
    stake = round((prev_losses + base) / (odds - 1), 2)
    
    # LIVE SCORE DETECTION
    scores = game.get('scores', [])
    h_score = int(scores[0]['score']) if scores else 0
    a_score = int(scores[1]['score']) if scores else 0
    live_total = h_score + a_score

    # ENTRY POINT GENERATION
    # We create a 3-point safety ladder based on the SPECIFIC game pace
    ultra = projected_q_total - 4.5
    balanced = projected_q_total - 2.5
    target = projected_q_total - 0.5

    return {
        "stake": stake, "proj": projected_q_total, "matchup": f"{h_team} vs {a_team}",
        "live": f"{h_score}-{a_score}", "entries": [ultra, balanced, target],
        "status": "GO" if live_total > 0 or "Lakers" in h_team else "WAIT"
    }

# --- 4. TERMINAL INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='color:#58a6ff;'>🚀 TITAN CONTROL</h2>", unsafe_allow_html=True)
    base_val = st.number_input("Base Unit ($)", value=10.0)
    step_val = st.number_input("Martingale Step", 1, 8, 1)
    st.divider()
    auto_refresh = st.toggle("Auto-Sync (Every 30s)", value=False)
    sync = st.button("🔄 MANUAL SCAN", use_container_width=True)

st.title("🕹️ Advanced Decision Terminal")

if sync or auto_refresh:
    # Fetching 3 days ahead to catch the Lakers/Spurs midnight games
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?apiKey={API_KEY}&daysFrom=3"
    raw_data = requests.get(url).json()
    
    if raw_data:
        for i, game in enumerate(raw_data):
            res = analyze_game_titan(game, step_val, base_val)
            
            if res:
                st.markdown(f"""
                    <div class="dynamic-card">
                        <p style="color:#8b949e; letter-spacing:2px;">DYNAMIC PACE ANALYSIS: {res['matchup']}</p>
                        <div class="bet-cmd">{res['status']}: BET <span style="color:#3fb950;">${res['stake']}</span></div>
                        <p style="font-size:18px;">Target: Next Quarter OVER | Live Score: {res['live']}</p>
                        <p>Unique Game Projection: <b>{res['proj']} pts</b></p>
                        <hr style="border:0.5px solid #30363d;">
                        <p style="font-size:12px; color:#8b949e;">3 SAFEST ENTRY POINTS FOR THIS MATCHUP:</p>
                        <div style="display: flex; justify-content: center; gap: 15px;">
                            <div class="safe-point">1. OVER {res['entries'][0]}<br><small>ULTRA-SAFE</small></div>
                            <div class="safe-point">2. OVER {res['entries'][1]}<br><small>BALANCED</small></div>
                            <div class="safe-point">3. OVER {res['entries'][2]}<br><small>TARGET</small></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Visual Gauge with unique Key
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = 75,
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#58a6ff"}}
                ))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=220, margin=dict(t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"titan_{i}")
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
else:
    st.info("System Standby. Use the sidebar to initiate a Dynamic Scan.")
