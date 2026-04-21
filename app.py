import streamlit as st
import pandas as pd

# --- 1. PRO DATASET (Points Per Minute - PPM) ---
# Average NBA quarter is 12 minutes. 
# 60 points per quarter = 5.0 Points Per Minute (PPM).
TEAM_PPM = {
    "Lakers": 4.8, 
    "Celtics": 5.2,
    "Nuggets": 5.0,
    "Warriors": 5.1
}

# --- 2. THE MOMENTUM CALCULATOR ---
def get_advanced_command(h_team, a_team, q_num, live_line, time_left, current_score, step, unit):
    # Calculate Expected Remaining Points
    h_ppm = TEAM_PPM.get(h_team, 4.8)
    a_ppm = TEAM_PPM.get(a_team, 4.8)
    combined_ppm = (h_ppm + a_ppm)
    
    projected_remaining = combined_ppm * time_left
    final_projection = current_score + projected_remaining
    
    # Martingale Math (Recovery + Target)
    odds = 1.91
    total_lost = sum([unit * (2**i) for i in range(step - 1)])
    stake = round((total_lost + unit) / (odds - 1), 2)
    
    # Decision Engine
    if final_projection > live_line + 2.5:
        direction = "OVER"
        strength = "HIGH"
    elif final_projection < live_line - 2.5:
        direction = "UNDER"
        strength = "HIGH"
    else:
        direction = "OVER" # Default to Over for excitement or 'Hold'
        strength = "LOW"

    return f"Hey, bet **${stake}** on **{q_num} Quarter {direction} {live_line} points**.", strength

# --- 3. THE UI ---
st.set_page_config(page_title="NBA Elite Terminal", layout="wide")

st.title("🦅 NBA Elite Command Terminal")

with st.sidebar:
    st.header("💰 Bankroll & Step")
    base_amt = st.number_input("Base Unit ($)", value=10.0)
    m_step = st.number_input("Martingale Step", min_value=1, max_value=6, value=1)
    if st.button("♻️ RESET STEP"):
        st.session_state.m_step = 1

col1, col2, col3 = st.columns(3)

with col1:
    h_t = st.selectbox("Home", list(TEAM_PPM.keys()))
    a_t = st.selectbox("Away", list(TEAM_PPM.keys()), index=1)

with col2:
    q_target = st.selectbox("Quarter", ["1st", "2nd", "3rd", "4th"])
    l_line = st.number_input("Live Line", value=55.5)

with col3:
    t_left = st.number_input("Minutes Remaining in Q", value=12.0, max_value=12.0)
    curr_s = st.number_input("Current Quarter Score", value=0)

st.divider()

# EXECUTION
instruction, power = get_advanced_command(h_t, a_t, q_target, l_line, t_left, curr_s, m_step, base_amt)

# High-Intensity Command Box
if power == "HIGH":
    color = "#00ff41" # Matrix Green
    border = "2px solid #00ff41"
else:
    color = "#ffcc00" # Warning Yellow
    border = "1px solid #ffcc00"

st.markdown(f"""
    <div style="background-color:#111; padding:30px; border-radius:15px; border: {border}; text-align:center;">
        <h1 style="color:{color}; font-family:monospace; letter-spacing: 2px;">{instruction}</h1>
        <p style="color:gray;">ANALYSIS STRENGTH: {power}</p>
    </div>
    """, unsafe_allow_html=True)

st.caption("Terminal v5.2 | Real-time Pace Variance Enabled")
