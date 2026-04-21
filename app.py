import streamlit as st
import pandas as pd

# --- 1. THE BRAIN: PACE & MOMENTUM ENGINE ---
TEAM_PROFILES = {
    "Lakers": {"PPM": 4.9, "Q_Trend": "High Pace 1st"},
    "Celtics": {"PPM": 5.1, "Q_Trend": "Elite 3rd"},
    "Nuggets": {"PPM": 4.8, "Q_Trend": "Consistent"},
}

def get_pro_instruction(h_team, a_team, q_num, live_line, time_left, current_pts, step, base_amt):
    # Calculate Expected Points for remaining time
    h_ppm = TEAM_PROFILES.get(h_team, {"PPM": 4.8})["PPM"]
    a_ppm = TEAM_PROFILES.get(a_team, {"PPM": 4.8})["PPM"]
    combined_expected_ppm = h_ppm + a_ppm
    
    projected_final = current_pts + (combined_expected_ppm * time_left)
    
    # Martingale Logic: (Previous Losses + Profit Goal) / (Odds - 1)
    odds = 1.91
    total_lost = sum([base_amt * (2**i) for i in range(step - 1)])
    stake = round((total_lost + base_amt) / (odds - 1), 2)
    
    # Logic Gate
    diff = projected_final - live_line
    if diff > 3.0:
        direction = "OVER"
        confidence = "HIGH"
    elif diff < -3.0:
        direction = "UNDER"
        confidence = "HIGH"
    else:
        direction = "OVER" # Default
        confidence = "LOW"
        
    instruction = f"Hey, bet **${stake}** on **{q_num} Quarter {direction} {live_line} points**."
    return instruction, confidence

# --- 2. ELITE INTERFACE ---
st.set_page_config(page_title="NBA Quantum Command", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #c9d1d9; }
    .reportview-container .main { background: #0b0e14; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 NBA Quantum Execution Terminal")

with st.sidebar:
    st.header("💳 Financial Logic")
    base = st.number_input("Base Unit ($)", value=10.0)
    step = st.number_input("Martingale Step", min_value=1, value=1)
    st.divider()
    st.info(f"Total Risked: **${sum([base * (2**i) for i in range(step)])}**")

col1, col2, col3 = st.columns(3)

with col1:
    h_t = st.selectbox("Home Team", list(TEAM_PROFILES.keys()))
    a_t = st.selectbox("Away Team", list(TEAM_PROFILES.keys()), index=1)

with col2:
    q_target = st.selectbox("Quarter", ["1st", "2nd", "3rd", "4th"])
    b_line = st.number_input("Current Live Line", value=55.5)

with col3:
    t_rem = st.slider("Minutes Left in Q", 0.0, 12.0, 12.0)
    c_score = st.number_input("Current Q-Score", value=0)

st.divider()

# --- THE COMMAND ---
command, conf = get_pro_instruction(h_t, a_t, q_target, b_line, t_rem, c_score, step, base)

if conf == "HIGH":
    st.balloons()
    border_color = "#00ff41" # Tactical Green
else:
    border_color = "#30363d" # Stealth Gray

st.markdown(f"""
    <div style="background-color:#161b22; padding:40px; border-radius:20px; border: 3px solid {border_color}; text-align:center;">
        <h1 style="color:white; font-family:monospace; font-size: 35px;">{command}</h1>
        <p style="color:#8b949e; font-size: 20px;">CONFIDENCE: {conf}</p>
    </div>
    """, unsafe_allow_html=True)
