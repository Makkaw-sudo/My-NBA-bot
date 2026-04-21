import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

# --- 1. PRO UI CONFIG ---
st.set_page_config(page_title="NBA QUANT-PRO TERMINAL", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #c9d1d9; }
    .main-card {
        background: linear-gradient(145deg, #161b22, #0d1117);
        padding: 35px;
        border-radius: 20px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .instruction-text {
        font-family: 'Courier New', monospace;
        color: #58a6ff;
        font-size: 32px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED ANALYTICS ENGINE ---
TEAM_STATS = {
    "Lakers": 2.48, "Celtics": 2.65, "Nuggets": 2.55, "Warriors": 2.61,
    "Suns": 2.52, "Bucks": 2.58, "Heat": 2.41, "76ers": 2.50,
    "Mavericks": 2.56, "Thunder": 2.60, "Knicks": 2.46, "Wolves": 2.44
}

def get_quant_analysis(h_team, a_team, live_line, time_left, current_score, step, base_unit):
    # Dynamic Pace Projection
    combined_ppm = TEAM_STATS.get(h_team, 2.5) + TEAM_STATS.get(a_team, 2.5)
    projected_remaining = combined_ppm * time_left
    final_projection = current_score + projected_remaining
    
    # Advanced Martingale Recovery (Targeting 5% ROI per sequence)
    odds = 1.91
    previous_losses = sum([base_unit * (2**i) for i in range(step - 1)])
    target_profit = base_unit * 1.05 
    stake = round((previous_losses + target_profit) / (odds - 1), 2)
    
    # Poisson Win Probability
    # Chance of total score landing OVER the line
    prob_over = (1 - poisson.cdf(live_line, final_projection)) * 100
    
    # Directional Edge
    edge = final_projection - live_line
    direction = "OVER" if edge > 0 else "UNDER"
    win_chance = prob_over if direction == "OVER" else (100 - prob_over)
    
    return stake, direction, round(win_chance, 1), round(final_projection, 1), edge

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    selected = option_menu(
        "TERMINAL", ["Live Ops", "Bankroll Shield", "Settings"],
        icons=['cpu', 'shield-lock', 'gear'], menu_icon="cast", default_index=0,
    )
    st.divider()
    base_val = st.number_input("Base Unit ($)", value=10.0)
    step_val = st.number_input("Martingale Step", min_value=1, max_value=7, value=1)
    st.write(f"**Step {step_val} Risk:** ${round(base_val * (2**(step_val-1)), 2)}")

# --- 4. LIVE OPERATIONS ---
if selected == "Live Ops":
    st.title("🕹️ Strategic Execution Terminal")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        home = st.selectbox("Home Team", list(TEAM_STATS.keys()))
        away = st.selectbox("Away Team", list(TEAM_STATS.keys()), index=1)
    with c2:
        q_num = st.selectbox("Quarter", ["1st", "2nd", "3rd", "4th"])
        line = st.number_input("Live O/U Line", value=55.5)
    with c3:
        minutes = st.slider("Minutes Left", 0.0, 12.0, 12.0)
        score = st.number_input("Current Quarter Score", value=0)

    st.divider()

    # Calculations
    stake, dir, prob, proj, edge_val = get_quant_analysis(home, away, line, minutes, score, step_val, base_val)

    # UI COMMAND CARD
    st.markdown(f"""
        <div class="main-card">
            <p style="text-align:center; color:#8b949e; margin-bottom:5px;">SYSTEM GENERATED INSTRUCTION</p>
            <div style="text-align:center;" class="instruction-text">
                Hey, bet <span style="color:#ffffff;">${stake}</span> on <br>
                {q_num} Quarter <span style="color:{'#00ff41' if dir=='OVER' else '#ff4560'};">{dir}</span> {line} points
            </div>
        </div>
    """, unsafe_allow_html=True)

    # PRO GAUGE CHART
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = prob,
        title = {'text': f"Win Probability ({dir})"},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#58a6ff"},
            'bgcolor': "#161b22",
            'steps': [
                {'range': [0, 50], 'color': '#30363d'},
                {'range': [50, 75], 'color': '#238636'},
                {'range': [75, 100], 'color': '#2ea043'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90}}))
    fig.update_layout(paper_bgcolor='#0b0e14', font={'color': "white", 'family': "Arial"}, height=300)
    st.plotly_chart(fig, use_container_width=True)

    # SUB-METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Projected Total", proj)
    m2.metric("Market Variance", f"{edge_val:+.1f} pts")
    m3.metric("Confidence", "HIGH" if abs(edge_val) > 2.5 else "MODERATE")

elif selected == "Bankroll Shield":
    st.header("🛡️ Sequence Risk Auditor")
    # Calculation of total debt in a 7-step sequence
    steps = list(range(1, 8))
    costs = [base_val * (2**(i-1)) for i in steps]
    
    df_risk = pd.DataFrame({'Step': steps, 'Bet Amount': costs})
    st.table(df_risk)
    st.error("⚠️ PRO TIP: If you reach Step 5, the mathematical probability of a 'bust' increases by 40%. Consider resetting to Step 1 to preserve capital.")
