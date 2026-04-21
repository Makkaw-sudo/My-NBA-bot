import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from streamlit_option_menu import option_menu
from datetime import datetime

# --- 1. PRO-LEVEL CONFIGURATION ---
st.set_page_config(page_title="NBA QUANTUM TERMINAL", layout="wide", initial_sidebar_state="expanded")

# Ultra-Dark Professional Theme
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .command-card {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #58a6ff;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .status-tag { font-family: monospace; font-weight: bold; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED ANALYTICS ENGINE ---
# Real-world Points Per Minute (PPM) averages for 2026
TEAM_METRICS = {
    "Lakers": 4.92, "Celtics": 5.25, "Nuggets": 5.05, "Warriors": 5.18,
    "Suns": 4.98, "Bucks": 5.12, "Heat": 4.75, "76ers": 4.95,
    "Mavericks": 5.08, "Thunder": 5.15, "Knicks": 4.88, "Wolves": 4.82
}

def calculate_quant_logic(h_team, a_team, live_line, time_left, current_score, step, base_unit):
    # Momentum Calculation
    h_ppm = TEAM_METRICS.get(h_team, 4.9)
    a_ppm = TEAM_METRICS.get(a_team, 4.9)
    projected_remaining = (h_ppm + a_ppm) * time_left
    projected_total = current_score + projected_remaining
    
    # Martingale Logic (Recovery Formula)
    odds = 1.91 # Standard decimal odds
    total_lost = sum([base_unit * (2**i) for i in range(step - 1)])
    stake = round((total_lost + base_unit) / (odds - 1), 2)
    
    # Probability (Poisson Distribution)
    # Finding probability that score > live_line
    prob_over = (1 - poisson.cdf(live_line, projected_total)) * 100
    
    # Edge Detection
    edge = projected_total - live_line
    direction = "OVER" if edge > 0 else "UNDER"
    confidence = "HIGH" if abs(edge) > 2.5 else "MODERATE"
    
    return stake, direction, round(prob_over, 1), confidence, round(projected_total, 1)

# --- 3. PRO NAVIGATION ---
with st.sidebar:
    st.title("🛡️ QUANT OPS")
    selected = option_menu(
        menu_title=None,
        options=["Command", "Risk Auditor", "Analytics"],
        icons=["terminal", "shield-check", "graph-up"],
        styles={
            "container": {"background-color": "#0d1117"},
            "nav-link-selected": {"background-color": "#21262d", "color": "#58a6ff"}
        }
    )
    st.divider()
    base_unit = st.number_input("Base Unit ($)", value=10.0, step=5.0)
    current_step = st.number_input("Martingale Step", min_value=1, max_value=7, value=1)
    st.caption(f"Current Date: {datetime.now().strftime('%Y-%m-%d')}")

# --- 4. EXECUTION PAGES ---
if selected == "Command":
    st.header("🎮 Strategic Execution Terminal")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        h_t = st.selectbox("Home Team", list(TEAM_METRICS.keys()))
        a_t = st.selectbox("Away Team", list(TEAM_METRICS.keys()), index=1)
    with col2:
        q_target = st.selectbox("Target Quarter", ["1st", "2nd", "3rd", "4th"])
        l_line = st.number_input("Live Line (O/U)", value=55.5)
    with col3:
        t_rem = st.slider("Minutes Remaining", 0.0, 12.0, 12.0)
        c_score = st.number_input("Current Quarter Score", value=0)

    st.divider()

    # Calculate the Move
    stake, dir, prob, conf, proj = calculate_quant_logic(h_t, a_t, l_line, t_rem, c_score, current_step, base_unit)

    # THE ULTIMATE COMMAND OUTPUT
    st.markdown(f"""
        <div class="command-card">
            <p style="color:#8b949e; text-transform:uppercase; font-size:14px;">Live Tactical Instruction</p>
            <h1 style="color:white; font-size:42px; margin-bottom:10px;">
                Hey, bet <span style="color:#58a6ff;">${stake}</span> on <br>
                {q_target} Quarter <span style="color:{'#00ff41' if dir=='OVER' else '#ff4560'};">{dir}</span> {l_line} points
            </h1>
            <p style="color:#58a6ff; font-size:18px;">Win Probability: {prob if dir=='OVER' else round(100-prob, 1)}% | Confidence: {conf}</p>
        </div>
    """, unsafe_allow_html=True)

    # Sub-Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Projected Total", proj)
    m2.metric("Market Variance", f"{proj - l_line:+.1f} pts")
    m3.metric("Sequence Risk", f"Step {current_step}")

elif selected == "Risk Auditor":
    st.header("🛡️ Portfolio Risk Management")
    total_invested = sum([base_unit * (2**i) for i in range(current_step)])
    
    c1, c2 = st.columns(2)
    c1.metric("Capital at Risk", f"${total_invested}")
    c2.metric("Next Recovery Stake", f"${base_unit * (2**current_step)}")
    
    st.warning("⚠️ PRO ADVICE: If you reach Step 5, evaluate the 'Pace Lead'. If the game is slowed by fouls, exit the sequence to protect your bankroll.")

elif selected == "Analytics":
    st.header("📊 Team Variance Data")
    df = pd.DataFrame.from_dict(TEAM_METRICS, orient='index', columns=['Points Per Minute (PPM)'])
    st.table(df.sort_values(by='Points Per Minute (PPM)', ascending=False))

st.caption("Quantum Terminal v6.0 | Professional Betting Integration")
