import streamlit as st
import pandas as pd
from scipy.stats import poisson
from streamlit_option_menu import option_menu

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="NBA Quantum Command", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #c9d1d9; }
    [data-testid="stMetricValue"] { color: #58a6ff; }
    .command-box {
        background-color: #161b22; 
        padding: 30px; 
        border-radius: 15px; 
        border: 2px solid #58a6ff; 
        text-align: center;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & PROBABILITY MATH ---
TEAM_PPM = {
    "Lakers": 4.85, "Celtics": 5.21, "Nuggets": 5.02, "Warriors": 5.15, 
    "Suns": 4.95, "Bucks": 5.10, "Heat": 4.70, "76ers": 4.90
}

def calculate_instruction(h_team, a_team, q_num, live_line, time_left, current_score, step, unit):
    # Calculate Projected Final Score for the Quarter
    h_ppm = TEAM_PPM.get(h_team, 4.9)
    a_ppm = TEAM_PPM.get(a_team, 4.9)
    projected_remaining = (h_ppm + a_ppm) * time_left
    final_projection = current_score + projected_remaining
    
    # Martingale Math: (Previous Losses + Target Profit) / (Odds - 1)
    odds = 1.91
    total_lost = sum([unit * (2**i) for i in range(step - 1)])
    stake = round((total_lost + unit) / (odds - 1), 2)
    
    # Probability Check (Poisson)
    prob_over = (1 - poisson.cdf(live_line, final_projection)) * 100
    
    # Direction Logic
    if final_projection > live_line + 1.5:
        direction = "OVER"
        confidence = "HIGH"
    elif final_projection < live_line - 1.5:
        direction = "UNDER"
        confidence = "HIGH"
    else:
        direction = "OVER" # Default
        confidence = "LOW"

    return f"Hey, bet **${stake}** on **{q_num} Quarter {direction} {live_line} points**.", confidence, round(prob_over, 1)

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    selected = option_menu(
        "Main Menu", ["Command Center", "Risk Auditor", "Settings"],
        icons=['terminal', 'shield-shaded', 'gear'], 
        menu_icon="cast", default_index=0,
    )
    st.divider()
    base_unit = st.number_input("Base Unit ($)", value=10.0)
    current_step = st.number_input("Martingale Step", min_value=1, max_value=8, value=1)

# --- 4. MAIN INTERFACE ---
if selected == "Command Center":
    st.title("🎯 NBA Execution Terminal")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        h_t = st.selectbox("Home Team", list(TEAM_PPM.keys()))
        a_t = st.selectbox("Away Team", list(TEAM_PPM.keys()), index=1)
    
    with col2:
        q_target = st.selectbox("Target Quarter", ["1st", "2nd", "3rd", "4th"])
        l_line = st.number_input("Live Bookie Line", value=55.5)
        
    with col3:
        t_rem = st.slider("Minutes Remaining", 0.0, 12.0, 12.0)
        c_score = st.number_input("Current Quarter Score", value=0)

    st.divider()

    # Generate the Instruction
    cmd, conf, prob = calculate_instruction(h_t, a_t, q_target, l_line, t_rem, c_score, current_step, base_unit)

    # Display the Result
    st.markdown(f"""
        <div class="command-box">
            <h1 style="color:white; font-size:32px;">{cmd}</h1>
            <p style="color:#8b949e;">Confidence: {conf} | Win Probability: {prob}%</p>
        </div>
    """, unsafe_allow_html=True)

    if conf == "HIGH":
        st.success("🔥 STRATEGIC OPPORTUNITY DETECTED")
    else:
        st.warning("⚖️ CAUTION: Projection is close to the line.")

elif selected == "Risk Auditor":
    st.title("🛡️ Risk Management")
    total_risk = sum([base_unit * (2**i) for i in range(current_step)])
    st.metric("Total Capital Risked in Current Run", f"${total_risk}")
    st.info("Remember: Martingale success depends on knowing when to walk away. Do not exceed 5 steps.")
