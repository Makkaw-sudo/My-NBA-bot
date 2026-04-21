import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

# --- 1. PRO INTERFACE CONFIG ---
st.set_page_config(page_title="NBA QUANTUM TERMINAL V8", layout="wide")

# High-End Dark Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .command-card {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 35px;
        border-radius: 20px;
        border: 2px solid #58a6ff;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }
    .instruction-header { font-family: monospace; color: #8b949e; letter-spacing: 2px; font-size: 14px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 2026 PLAYOFF ANALYTICS ENGINE ---
# Calibrated for Playoff Intensity (Points Per Minute)
TEAM_METRICS = {
    "Lakers": 2.48, "Celtics": 2.65, "76ers": 2.47, "Spurs": 2.42,
    "Rockets": 2.51, "Nuggets": 2.55, "Warriors": 2.61, "Suns": 2.52,
    "Bucks": 2.58, "Thunder": 2.60, "Knicks": 2.46, "Wolves": 2.44
}

def calculate_quant_logic(h_team, a_team, live_line, time_left, current_score, step, base_unit, bench_mode):
    # Adjust pace if bench is on the floor (usually -15%)
    rotation_impact = 0.85 if bench_mode else 1.0
    combined_ppm = (TEAM_METRICS.get(h_team, 2.5) + TEAM_METRICS.get(a_team, 2.5)) * rotation_impact
    
    # Projection = What happened + (Pace * Remaining Time)
    projected_remaining = combined_ppm * time_left
    final_projection = current_score + projected_remaining
    
    # Martingale Recovery (Targeting Profit + covering previous losses)
    odds = 1.91 
    total_lost = sum([base_unit * (2**i) for i in range(step - 1)])
    stake = round((total_lost + base_unit) / (odds - 1), 2)
    
    # Poisson Win Probability
    prob_over = (1 - poisson.cdf(live_line, final_projection)) * 100
    
    # Directional Edge
    edge = final_projection - live_line
    direction = "OVER" if edge > 0 else "UNDER"
    win_chance = prob_over if direction == "OVER" else (100 - prob_over)
    
    # Confidence Level
    if abs(edge) > 3.5: confidence = "ELITE"
    elif abs(edge) > 2.0: confidence = "STRONG"
    else: confidence = "MODERATE"
    
    return stake, direction, round(win_chance, 1), confidence, round(final_projection, 1), round(edge, 1)

# --- 3. PRO NAVIGATION ---
with st.sidebar:
    st.title("🛡️ QUANT OPS")
    selected = option_menu(
        menu_title=None,
        options=["Terminal", "Risk Auditor", "2026 Playoffs"],
        icons=["terminal", "shield-lock", "trophy"],
        styles={"container": {"background-color": "#0d1117"}}
    )
    st.divider()
    base_unit = st.number_input("Base Unit ($)", value=10.0, step=5.0)
    current_step = st.number_input("Martingale Step", min_value=1, max_value=8, value=1)
    
    st.subheader("Live Modifiers")
    bench_active = st.toggle("Bench Rotation Active", value=False)
    st.caption("Enable if star players are resting.")

# --- 4. EXECUTION PAGES ---
if selected == "Terminal":
    st.header("🎮 Strategic Execution Terminal")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        h_t = st.selectbox("Home Team", list(TEAM_METRICS.keys()))
        a_t = st.selectbox("Away Team", list(TEAM_METRICS.keys()), index=4) # Default to Rockets
    with col2:
        q_target = st.selectbox("Quarter", ["1st", "2nd", "3rd", "4th"])
        l_line = st.number_input("Live Bookie Line", value=55.5)
    with col3:
        t_rem = st.slider("Minutes Remaining", 0.0, 12.0, 12.0)
        c_score = st.number_input("Current Quarter Score", value=0)

    st.divider()

    # Calculate Logic
    stake, dir, prob, conf, proj, edge_val = calculate_quant_logic(h_t, a_t, l_line, t_rem, c_score, current_step, base_unit, bench_active)

    # THE ULTIMATE COMMAND CARD
    st.markdown(f"""
        <div class="command-card">
            <p class="instruction-header">Tactical Instruction Generated</p>
            <h1 style="color:white; font-size:42px; margin-bottom:10px;">
                Hey, bet <span style="color:#58a6ff;">${stake}</span> on <br>
                {q_target} Quarter <span style="color:{'#00ff41' if dir=='OVER' else '#ff4560'};">{dir}</span> {l_line} points
            </h1>
            <p style="color:#58a6ff; font-size:18px;">Win Probability: {prob}% | Confidence: {conf}</p>
        </div>
    """, unsafe_allow_html=True)

    # VISUAL PROBABILITY GAUGE
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = prob,
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#58a6ff"},
            'steps': [
                {'range': [0, 50], 'color': '#30363d'},
                {'range': [50, 80], 'color': '#238636'}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': 90}}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300, margin=dict(t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # REALITY CHECK METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Projected Total", proj)
    m2.metric("Market Variance", f"{edge_val:+.1f} pts")
    m3.metric("Current Run", f"Step {current_step}")

elif selected == "Risk Auditor":
    st.header("🛡️ Portfolio Risk")
    total_invested = sum([base_unit * (2**i) for i in range(current_step)])
    st.metric("Total Capital Risked", f"${total_invested}")
    st.warning("Martingale safety check: Sequence probability of failure at Step 5 is ~3.1%.")

elif selected == "2026 Playoffs":
    st.header("🏆 Playoff Schedule")
    st.info("76ers vs Celtics | Blazers vs Spurs | Rockets vs Lakers")
