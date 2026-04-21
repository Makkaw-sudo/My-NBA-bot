import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time

# --- 1. SETTINGS & HIGH-END TERMINAL THEME ---
st.set_page_config(page_title="QUANTUM TITAN V11", layout="wide")

st.markdown("""
    <style>
    /* Main Background & Font */
    .stApp { background-color: #05070a; color: #e6edf3; font-family: 'Inter', sans-serif; }
    
    /* The Cockpit Card */
    .titan-card {
        background: linear-gradient(160deg, #0d1117 0%, #161b22 100%);
        padding: 25px; 
        border-radius: 15px; 
        border-left: 5px solid #58a6ff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }

    /* Glowing Signal for "GO" */
    .signal-go {
        color: #3fb950;
        font-size: 48px;
        font-weight: 900;
        text-shadow: 0 0 20px rgba(63, 185, 80, 0.4);
        font-family: 'Courier New', monospace;
        margin: 10px 0;
    }
    
    .signal-wait {
        color: #8b949e;
        font-size: 48px;
        font-weight: 900;
        font-family: 'Courier New', monospace;
        margin: 10px 0;
    }

    /* The 'Safe Ladder' Boxes */
    .ladder-box {
        background: #0d1117;
        border: 1px solid #30363d;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        min-width: 110px;
    }

    /* Value Badge */
    .value-badge {
        background-color: rgba(56, 139, 253, 0.15);
        color: #58a6ff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: bold;
        border: 1px solid #58a6ff;
    }

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION & DATA DNA ---
API_KEY = "4d1e72e9dc2207f0ae744c61dfa51576"

TEAM_PACE = {
    "Los Angeles Lakers": 29.8, "Houston Rockets": 27.5,
    "San Antonio Spurs": 29.1, "Portland Trail Blazers": 26.9,
    "Cleveland Cavaliers": 27.2, "Toronto Raptors": 28.4,
    "New York Knicks": 26.5, "Atlanta Hawks": 30.2,
    "Boston Celtics": 30.5, "Philadelphia 76ers": 28.8
}

# --- 3. ANALYTICS ENGINE (KELLY + PACE LOGIC) ---
def calculate_kelly(prob, odds):
    b = odds - 1
    q = 1 - prob
    return max(0, (b * prob - q) / b)

def analyze_game_titan(game, step, base, schedule_type, my_win_prob, bankroll, kelly_fraction):
    h_team = game.get('home_team')
    a_team = game.get('away_team')
    
    # Apply Fatigue Factor
    fatigue_mod = 0.96 if schedule_type == "Tired (B2B/3in4)" else 1.0
    
    h_pace = TEAM_PACE.get(h_team, 28.5)
    a_pace = TEAM_PACE.get(a_team, 28.5)
    projected_q_total = round((h_pace + a_pace) * fatigue_mod, 1)

    # Recovery Logic (Martingale)
    odds_1xbet = 1.91 
    prev_losses = sum([base * (2**i) for i in range(step - 1)])
    m_stake = round((prev_losses + base) / (odds_1xbet - 1), 2)
    
    # Kelly Logic (Value Betting)
    kelly_pct = calculate_kelly(my_win_prob / 100, odds_1xbet)
    k_stake = round(bankroll * kelly_pct * kelly_fraction, 2)

    # Edge Analysis
    implied_prob = (1 / odds_1xbet) * 100
    is_value = my_win_prob > implied_prob
    
    # Live Status
    scores = game.get('scores', [])
    h_score = int(scores[0]['score']) if scores else 0
    a_score = int(scores[1]['score']) if scores else 0
    
    # Target Lines
    entries = [projected_q_total - 4.5, projected_q_total - 2.5, projected_q_total - 0.5]

    return {
        "m_stake": m_stake, "k_stake": k_stake, 
        "proj": projected_q_total, "matchup": f"{h_team} vs {a_team}",
        "live": f"{h_score}-{a_score}", "entries": entries,
        "is_value": is_value, "val_gap": round(my_win_prob - implied_prob, 1),
        "status": "GO" if is_value and (h_score + a_score > 0 or "Lakers" in h_team) else "WAIT"
    }

# --- 4. TERMINAL INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='color:#58a6ff;'>🚀 TITAN CONTROL</h2>", unsafe_allow_html=True)
    bankroll_total = st.number_input("Bankroll ($)", value=1000.0)
    base_val = st.number_input("Base Unit ($)", value=10.0)
    step_val = st.number_input("Martingale Step", 1, 8, 1)
    
    st.divider()
    st.markdown("### 🧠 STRONG ANALYSIS")
    sched = st.selectbox("Schedule Status", ["Normal/Rested", "Tired (B2B/3in4)"])
    win_p = st.slider("My Win Probability (%)", 30, 95, 55)
    kelly_f = st.slider("Kelly Fraction", 0.1, 1.0, 0.5)
    
    st.divider()
    auto_refresh = st.toggle("Auto-Sync (30s)", value=False)
    sync = st.button("🔄 INITIATE SCAN", use_container_width=True)

# Page Header
st.markdown("<h1 style='text-align: center; color: #58a6ff; letter-spacing: 5px; margin-bottom:0;'>QUANTUM TITAN V11</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e; margin-bottom:40px;'>PACE-DRIVEN PROBABILISTIC ANALYSIS ENGINE</p>", unsafe_allow_html=True)

if sync or auto_refresh:
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?apiKey={API_KEY}&daysFrom=3"
    try:
        raw_data = requests.get(url).json()
        
        if raw_data:
            cols = st.columns(2)
            for i, game in enumerate(raw_data):
                res = analyze_game_titan(game, step_val, base_val, sched, win_p, bankroll_total, kelly_f)
                
                with cols[i % 2]:
                    # Dynamic Visual Card
                    status_class = "signal-go" if res['status'] == "GO" else "signal-wait"
                    val_color = "#3fb950" if res['is_value'] else "#f85149"
                    
                    st.markdown(f"""
                        <div class="titan-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #8b949e; font-family: monospace; font-size:12px;">STREAMING // {res['matchup']}</span>
                                <span class="value-badge" style="border-color:{val_color}; color:{val_color};">EDGE: {res['val_gap']}%</span>
                            </div>
                            
                            <div style="padding: 15px 0;">
                                <div style="color: {val_color}; font-size: 11px; letter-spacing: 2px;">SYSTEM_STATUS: {res['status']}</div>
                                <div class="{status_class}">BET ${res['k_stake'] if res['status'] == "GO" else "0.00"}</div>
                                <div style="color: #f0f6fc; font-size: 16px;">Target Quarter Over: <span style="color:#58a6ff;">{res['entries'][1]}</span></div>
                            </div>

                            <div style="display: flex; gap: 10px; justify-content: center; margin-top: 10px;">
                                <div class="ladder-box"><small style="color:#8b949e;">ULTRA</small><br><b style="color:#3fb950;">{res['entries'][0]}</b></div>
                                <div class="ladder-box"><small style="color:#8b949e;">BALANCED</small><br><b>{res['entries'][1]}</b></div>
                                <div class="ladder-box"><small style="color:#8b949e;">RISKY</small><br><b style="color:#f85149;">{res['entries'][2]}</b></div>
                            </div>
                            
                            <div style="margin-top: 20px; font-size: 11px; color: #8b949e; font-family: monospace;">
                                PACE_PROJ: {res['proj']} | LIVE: {res['live']} | STRAT: KELLY_{kelly_f}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No active games found for the selected period.")
            
    except Exception as e:
        st.error(f"API Connection Error: {e}")
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
else:
    st.info("System on Standby. Initiate Scan from the Titan Control sidebar.")
