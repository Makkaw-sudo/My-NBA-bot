import streamlit as st
import math
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION ---
BANKROLL = 5000.00
BASE_BET = 100.00
MAX_RISK_LIMIT = 0.15 

# --- 2. MATH ENGINE ---
def calculate_safety_and_profit(step, odds, line, expected):
    current_stake = BASE_BET * (2 ** step)
    total_wagered = sum([BASE_BET * (2**i) for i in range(step + 1)])
    
    # Probability Logic (Z-Score)
    std_dev = 4.5
    z_score = (line - expected) / std_dev
    prob = 0.5 * (1 + math.erf(-z_score / math.sqrt(2)))
    
    potential_return = current_stake * odds
    net_profit = potential_return - total_wagered
    is_danger = total_wagered > (BANKROLL * MAX_RISK_LIMIT)
    
    return round(prob * 100, 1), current_stake, round(net_profit, 2), is_danger, total_wagered

# --- 3. UI STYLING ---
st.set_page_config(page_title="NBA SOVEREIGN", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .instruction-card {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border: 1px solid #30363d;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'history' not in st.session_state: st.session_state.history = []

# --- 5. INPUT SECTION (LEADS) ---
with st.sidebar:
    st.header("🎯 Live Lead Entry")
    game_name = st.text_input("Game", "Lakers vs Warriors")
    expected_pts = st.number_input("Expected Points (Model)", value=61.5)
    current_line = st.number_input("Bookie Line (Current)", value=54.5)
    current_odds = st.number_input("Live Odds", value=2.3)

# Run Math
prob, stake, profit, danger, total_at_risk = calculate_safety_and_profit(
    st.session_state.step, current_odds, current_line, expected_pts
)

# --- 6. MAIN DISPLAY ---
st.title("🛡️ Sovereign Strategy Terminal")

col_main, col_stats = st.columns([2, 1])

with col_main:
    # Execution Instruction
    status_color = "#ff7b72" if danger else "#58a6ff"
    
    st.markdown(f"""
        <div class="instruction-card">
            <h1 style="color: white; margin-top: 0;">{game_name}</h1>
            <p style="color: #8b949e;">SEQUENCE STEP: {st.session_state.step + 1}</p>
            <hr style="border: 0.5px solid #30363d;">
            <div style="padding: 20px 0;">
                <span style="color: #8b949e; font-size: 1.2em;">COMMAND:</span><br>
                <span style="font-size: 3.5em; font-weight: 800; color: white;">BET <span style="color: {status_color};">OVER {current_line}</span></span>
            </div>
            <div style="display: flex; gap: 40px;">
                <div><small style="color: #8b949e;">REQUIRED STAKE</small><br><b style="font-size: 1.5em;">${stake}</b></div>
                <div><small style="color: #8b949e;">TARGET PROFIT</small><br><b style="font-size: 1.5em; color: #3fb950;">+${profit}</b></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons
    st.write("")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("✅ WIN: RESET SEQUENCE", use_container_width=True):
            st.session_state.history.append({"Game": game_name, "Result": "WIN", "Profit": profit})
            st.session_state.step = 0
            st.balloons()
            st.rerun()
    with b2:
        if st.button("❌ LOSS: ESCALATE", use_container_width=True):
            st.session_state.step += 1
            st.rerun()

with col_stats:
    st.subheader("📊 Performance & Risk")
    
    # Bankroll Risk Bar
    risk_pct = (total_at_risk / BANKROLL)
    st.write(f"Bankroll Risk: {round(risk_pct*100, 1)}%")
    st.progress(min(risk_pct, 1.0))
    
    st.metric("Win Probability", f"{prob}%", delta=f"{round(prob-50, 1)}% vs Coin Flip")
    
    if danger:
        st.warning("⚠️ CRITICAL RISK: Bankroll protection engaged. Stop doubling.")

    # History Expander
    with st.expander("📝 Session History"):
        if st.session_state.history:
            st.table(pd.DataFrame(st.session_state.history))
        else:
            st.write("No games logged yet.")
