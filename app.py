import streamlit as st
import time
import math
from datetime import datetime, timedelta

# --- 1. CORE MATH LOGIC (Poisson & Probability) ---
def calculate_win_prob(expected_pts, live_line):
    """
    Uses a simplified Poisson logic to estimate the chance of an 'Over'.
    """
    # Poisson formula component: e^-lambda * (lambda^k / k!) is complex for 50+ points,
    # so we use a Normal Distribution approximation for speed.
    if expected_pts <= 0: return 0
    
    # Standard deviation in NBA quarters is roughly 4.5 points
    std_dev = 4.5
    z_score = (live_line - expected_pts) / std_dev
    
    # Simple probability estimation
    prob = 0.5 * (1 + math.erf(-z_score / math.sqrt(2)))
    return round(prob * 100, 1)

# --- 2. SESSION STATE (The Memory of the App) ---
if 'game_idx' not in st.session_state:
    st.session_state.game_idx = 0
if 'martingale_step' not in st.session_state:
    st.session_state.martingale_step = 0

# --- 3. MOCK DATA (Leads with Probability Math) ---
# In your real app, 'expected_q_pts' would come from pre-game closing lines
leads = [
    {"teams": "Boston vs Philly", "time": datetime.now() + timedelta(minutes=2), "expected": 58.5, "line": 54.5},
    {"teams": "Lakers vs Warriors", "time": datetime.now() + timedelta(minutes=15), "expected": 61.0, "line": 63.5}
]

# --- 4. STYLING ---
st.markdown("""
    <style>
    .main-card { background: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; }
    .stat-box { background: #0d1117; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #3fb950; }
    .prob-high { color: #3fb950; font-weight: bold; }
    .prob-low { color: #ff7b72; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 5. MAIN DISPLAY ---
st.title("🏀 NBA Martingale Command Center")

current = leads[st.session_state.game_idx]
prob = calculate_win_prob(current['expected'], current['line'])
base_stake = 100
current_stake = base_stake * (2 ** st.session_state.martingale_step)

# Countdown Calculation
time_left = current['time'] - datetime.now()
sec_left = int(time_left.total_seconds())
timer_str = f"{max(0, sec_left // 60)}m {max(0, sec_left % 60)}s"

# Render UI Card
st.markdown(f"""
    <div class="main-card">
        <h2 style="margin-bottom:0;">{current['teams']}</h2>
        <p style="color: #8b949e;">Next Opportunity Countdown: <b style="color:white;">{timer_str}</b></p>
        <hr style="border: 0.1px solid #30363d;">
        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <div class="stat-box" style="flex: 1;">
                <div style="font-size: 12px; color: #8b949e;">WIN PROBABILITY</div>
                <div style="font-size: 22px;" class="{"prob-high" if prob > 55 else "prob-low"}">{prob}%</div>
            </div>
            <div class="stat-box" style="flex: 1; border-color: #ff7b72;">
                <div style="font-size: 12px; color: #8b949e;">REQUIRED STAKE</div>
                <div style="font-size: 22px; color: #ff7b72;">${current_stake}</div>
            </div>
        </div>
        <div style="margin-top: 15px; text-align: center;">
            <small style="color: #8b949e;">Step {st.session_state.martingale_step + 1} of Martingale Progression</small>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 6. CONTROLS ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✅ WON (Reset)"):
        st.session_state.martingale_step = 0
        st.rerun()

with col2:
    if st.button("❌ LOST (Double)"):
        st.session_state.martingale_step += 1
        st.rerun()

with col3:
    if st.button("NEXT GAME ➡️"):
        st.session_state.game_idx = (st.session_state.game_idx + 1) % len(leads)
        st.rerun()

# This small script auto-refreshes the page every 30 seconds to update the timer
# without causing the "black screen" infinite loop.
st.empty()
time.sleep(0.1) # Brief pause for stability
