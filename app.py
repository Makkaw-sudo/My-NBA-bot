import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time

# --- 1. SETTINGS & DYNAMIC THEME ---
st.set_page_config(page_title="QUANTUM TITAN V11 - PRO", layout="wide")
API_KEY = "4d1e72e9dc2207f0ae744c61dfa51576"

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e6edf3; }
    .dynamic-card {
        background: linear-gradient(135deg, #1e2631 0%, #0d1117 100%);
        padding: 35px; border-radius: 25px; border: 2px solid #58a6ff;
        text-align: center; box-shadow: 0 15px 50px rgba(0,0,0,0.9);
        margin-bottom: 20px;
    }
    .bet-cmd { font-size: 52px; font-weight: 900; color: #ffffff; }
    .value-tag { color: #3fb950; font-weight: bold; border: 1px solid #3fb950; padding: 5px 10px; border-radius: 5px; }
    .safe-point { background: #161b22; padding: 12px; border-radius: 10px; border: 1px solid #3fb950; color: #3fb950; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED PACE DATABASE ---
TEAM_PACE = {
    "Los Angeles Lakers": 29.8, "Houston Rockets": 27.5,
    "San Antonio Spurs": 29.1, "Portland Trail Blazers": 26.9,
    "Cleveland Cavaliers": 27.2, "Toronto Raptors": 28.4,
    "New York Knicks": 26.5, "Atlanta Hawks": 30.2,
    "Boston Celtics": 30.5, "Philadelphia 76ers": 28.8
}

# --- 3. STRONG ANALYSIS CALCULATORS ---
def calculate_kelly(prob, odds):
    b = odds - 1
    q = 1 - prob
    return max(0, (b * prob - q) / b)

# --- 4. THE ANALYTICS ENGINE (DYNAMIC V2) ---
def analyze_game_titan(game, step, base, schedule_type, my_win_prob, bankroll, kelly_fraction):
    h_team = game.get('home_team')
    a_team = game.get('away_team')
    
    # FATIGUE MULTIPLIER (Strong Analysis Factor)
    # If a team is on a back-to-back, we reduce the expected scoring pace
    fatigue_mod = 0.96 if schedule_type == "Tired (B2B/3in4)" else 1.0
    
    h_pace = TEAM_PACE.get(h_team, 28.5)
    a_pace = TEAM_PACE.get(a_team, 28.5)
    projected_q_total = round((h_pace + a_pace) * fatigue_mod, 1)

    # RECOVERY CALC (Martingale)
    odds_1xbet = 1.91 
    prev_losses = sum([base * (2**i) for i in range(step - 1)])
    martingale_stake = round((prev_losses + base) / (odds_1xbet - 1), 2)
    
    # KELLY CRITERION CALC (Scientific Stake)
    kelly_pct = calculate_kelly(my_win_prob / 100, odds_1xbet)
    kelly_stake = round(bankroll * kelly_pct * kelly_fraction, 2)

    # VALUE DETECTION
    implied_prob = (1 / odds_1xbet) * 100
    is_value = my_win_prob > implied_prob

    # LIVE SCORE DETECTION
    scores = game.get('scores', [])
    h_score = int(scores[0]['score']) if scores else 0
    a_score = int(scores[1]['score']) if scores else 0
    live_total = h_score + a_score

    # ENTRY POINT LADDER
    ultra = projected_q_total - 4.5
    balanced = projected_q_total - 2.5
    target = projected_q_total - 0.5

    return {
        "m_stake": martingale_stake, "k_stake": kelly_stake, 
        "proj": projected_q_total, "matchup": f"{h_team} vs {a_team}",
        "live": f"{h_score}-{a_score}", "entries": [ultra, balanced, target],
        "is_value": is_value, "val_gap": round(my_win_prob - implied_prob, 1),
        "status": "GO" if is_value and (live_total > 0 or "Lakers" in h_team) else "WAIT"
    }

# --- 5. TERMINAL INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='color:#58a6ff;'>🚀 TITAN CONTROL</h2>", unsafe_allow_html=True)
    bankroll_total = st.number_input("Total Bankroll ($)", value=1000.0)
    base_val = st.number_input("Base Unit ($)", value=10.0)
    step_val = st.number_input("Martingale Step", 1, 8, 1)
    
    st.divider()
    st.markdown("### 🧠 STRONG ANALYSIS")
    sched = st.selectbox("Schedule Status", ["Normal/Rested", "Tired (B2B/3in4)"])
    win_p = st.slider("My Win Probability (%)", 30, 90, 55)
    kelly_f = st.slider("Kelly Safety (0.5 = Half Kelly)", 0.1, 1.0, 0.5)
    
    st.divider()
    auto_refresh = st.toggle("Auto-Sync (Every 30s)", value=False)
    sync = st.button("🔄 MANUAL SCAN", use_container_width=True)

st.title("🕹️ Advanced Decision Terminal")

if sync or auto_refresh:
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?apiKey={API_KEY}&daysFrom=3"
    raw_data = requests.get(url).json()
    
    if raw_data:
        for i, game in enumerate(raw_data):
            res = analyze_game_titan(game, step_val, base_val, sched, win_p, bankroll_total, kelly_f)
            
            if res:
                # Value Indicator
                val_text = f"VALUE DETECTED (+{res['val_gap']}%)" if res['is_value'] else "NO VALUE"
                val_color = "#3fb950" if res['is_value'] else "#f85149"

                st.markdown(f"""
                    <div class="dynamic-card">
                        <p style="color:#8b949e; letter-spacing:2px;">DYNAMIC PACE ANALYSIS: {res['matchup']}</p>
                        <div style="margin-bottom:10px;"><span class="value-tag" style="border-color:{val_color}; color:{val_color};">{val_text}</span></div>
                        <div class="bet-cmd">{res['status']}: BET <span style="color:#3fb950;">${res['k_stake']}</span></div>
                        <p style="font-size:18px;">Strategy: Kelly Stake (${res['k_stake']}) vs Martingale (${res['m_stake']})</p>
                        <p>Unique Game Projection: <b>{res['proj']} pts</b> (Adj. for {sched})</p>
                        <hr style="border:0.5px solid #30363d;">
                        <p style="font-size:12px; color:#8b949e;">3 SAFEST ENTRY POINTS FOR THIS MATCHUP:</p>
                        <div style="display: flex; justify-content: center; gap: 15px;">
                            <div class="safe-point">1. OVER {res['entries'][0]}<br><small>ULTRA-SAFE</small></div>
                            <div class="safe-point">2. OVER {res['entries'][1]}<br><small>BALANCED</small></div>
                            <div class="safe-point">3. OVER {res['entries'][2]}<br><small>TARGET</small></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Confidence Gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = win_p,
                    title = {'text': "Confidence Score"},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#58a6ff"}}
                ))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=220, margin=dict(t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"titan_{i}")
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
else:
    st.info("System Standby. Adjust 'My Win Probability' in the sidebar and initiate Scan.")
