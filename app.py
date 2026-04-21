import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

# --- 1. THE "ULTIMATE" UI STYLING ---
st.set_page_config(page_title="NBA QUANTUM TERMINAL", layout="wide")

st.markdown("""
    <style>
    /* Professional Dark Theme */
    .stApp { background-color: #0b0e14; color: #e6edf3; }
    
    /* Neon Execution Card */
    .execution-card {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #58a6ff;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.7);
        margin-top: 10px;
    }
    
    /* Command Text Styling */
    .cmd-header { font-family: 'Courier New', monospace; color: #8b949e; letter-spacing: 3px; font-size: 14px; margin-bottom: 20px; }
    .cmd-main { font-size: 44px; font-weight: 800; line-height: 1.2; margin-bottom: 20px; }
    .highlight { color: #58a6ff; }
    
    /* Metric Blocks */
    .metric-box {
        background: #161b22;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ELITE PREDICTION ENGINE ---
TEAM_METRICS = {
    "Lakers": 2.48, "Celtics": 2.65, "76ers": 2.47, "Spurs": 2.42,
    "Rockets": 2.51, "Nuggets": 2.55, "Warriors": 2.61, "Suns": 2.52,
    "Bucks": 2.58, "Thunder": 2.60, "Knicks": 2.46, "Wolves": 2.44
}

def get_pro_logic(h_team, a_team, live_line, time_left, current_score, step, base_unit, bench_active):
    # Contextual Pace Adjustment
    rotation_factor = 0.82 if bench_active else 1.0
    combined_ppm = (TEAM_METRICS.get(h_team, 2.5) + TEAM_METRICS.get(a_team, 2.5)) * rotation_factor
    
    # Projection
    final_proj = current_score + (combined_ppm * time_left)
    
    # Martingale Recovery
    odds = 1.91 
    lost = sum([base_unit * (2**i) for i in range(step - 1)])
    stake = round((lost + base_unit) / (odds - 1), 2)
    
    # Poisson Math
    prob_over = (1 - poisson.cdf(live_line, final_proj)) * 100
    
    # Signal Logic
    edge = final_proj - live_line
    direction = "OVER" if edge > 0 else "UNDER"
    win_pct = prob_over if direction == "OVER" else (100 - prob_over)
    
    conf = "ELITE" if abs(edge) > 3.8 else ("STRONG" if abs(edge) > 2.2 else "NEUTRAL")
    
    return stake, direction, round(win_pct, 1), conf, round(final_proj, 1), round(edge, 1)

# --- 3. PRO NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color:#58a6ff;'>🛡️ QUANT OPS</h2>", unsafe_allow_html=True)
    selected = option_menu(
        None, ["Terminal", "Risk Management", "2026 Playoffs"],
        icons=['terminal', 'shield-lock', 'trophy'], 
        default_index=0, styles={"container": {"background-color": "#0d1117"}}
    )
    st.divider()
    base_val = st.number_input("Base Unit ($)", value=10.0, step=5.0)
    step_val = st.number_input("Martingale Step", min_value=1, max_value=8, value=1)
    bench_on = st.toggle("Bench Rotation Active", value=False)
    st.caption("Star players resting? Enable for accuracy.")

# --- 4. TERMINAL PAGE ---
if selected == "Terminal":
    st.title("🕹️ High-Frequency Terminal")
    
    # Input Row
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    with row1_c1:
        h_t = st.selectbox("Home Team", list(TEAM_METRICS.keys()))
        a_t = st.selectbox("Away Team", list(TEAM_METRICS.keys()), index=4)
    with row1_c2:
        q_target = st.selectbox("Quarter", ["1st", "2nd", "3rd", "4th"])
        l_line = st.number_input("Live O/U Line", value=55.5)
    with row1_c3:
        t_rem = st.slider("Minutes Left", 0.0, 12.0, 12.0)
        c_score = st.number_input("Current Score", value=0)

    # Calculation Execution
    stake, dir, prob, conf, proj, edge = get_pro_logic(h_t, a_t, l_line, t_rem, c_score, step_val, base_val, bench_on)

    # THE MAIN COMMAND CARD (AS REQUESTED)
    st.markdown(f"""
        <div class="execution-card">
            <div class="cmd-header">STRATEGIC COMMAND AUTHORIZED</div>
            <div class="cmd-main">
                Hey, bet <span class="highlight">${stake}</span> on <br>
                {q_target} Quarter <span style="color:{'#3fb950' if dir=='OVER' else '#f85149'};">{dir}</span> {l_line} points
            </div>
            <div style="color:#58a6ff; font-weight:bold; letter-spacing:1px;">
                PROBABILITY: {prob}% | SIGNAL: {conf}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # THE PRO GAUGE
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = prob,
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#58a6ff"},
            'steps': [{'range': [0, 50], 'color': '#21262d'}, {'range': [50, 100], 'color': '#238636'}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': 90}}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=280, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # SECONDARY METRIC GRID
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-box"><small>Projected Total</small><br><b style="font-size:24px;">{proj}</b></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-box"><small>Market Edge</small><br><b style="font-size:24px; color:#3fb950;">{edge:+.1f} pts</b></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-box"><small>Exposure</small><br><b style="font-size:24px;">Step {step_val}</b></div>', unsafe_allow_html=True)

elif selected == "Risk Management":
    st.header("🛡️ Sequence Auditor")
    # Show bankroll math here...
    st.info("Ensure you have enough liquid funds to cover up to Step 6 ($640.00 for a $10 base).")

elif selected == "2026 Playoffs":
    st.header("🏆 Live Playoff Context")
    st.write("Current Matchups: **Celtics (1-0)**, **Spurs (1-0)**, **Lakers (1-0)**.")
