import streamlit as st
import pandas as pd
import numpy as np

# --- 1. PROBABILITY LOGIC ---
def calculate_failure_risk(prob_win_per_q, quarters_left):
    prob_loss_per_q = 1 - (prob_win_per_q / 100)
    return round((prob_loss_per_q ** quarters_left) * 100, 2)

def martingale_recovery(initial_stake, total_loss, odds):
    return round((total_loss + initial_stake) / (odds - 1), 2)

# --- 2. APP UI SETUP ---
st.set_page_config(page_title="NBA Analytics", layout="wide")
st.title("🏀 NBA Game & Martingale Analyzer")

with st.sidebar:
    st.header("Strategy Settings")
    base_unit = st.number_input("Base Unit Stake", min_value=1.0, value=10.0)
    st.info("Targeting Over 55.5 points per quarter.")

# --- 3. MAIN PAGE: DAILY GAMES ---
st.header("📅 Daily Game Analysis")

daily_games = [
    {"Game": "Celtics @ 76ers", "Over Prob": 58.2, "Odds": 1.88},
    {"Game": "Suns @ OKC", "Over Prob": 55.5, "Odds": 1.91},
    {"Game": "Lakers @ Rockets", "Over Prob": 52.1, "Odds": 1.95},
]

df = pd.DataFrame(daily_games)

# The "FIX": Using .map instead of .applymap
def highlight_safe(val):
    if isinstance(val, float) and val >= 55.0:
        return 'background-color: #2e7d32; color: white'
    return ''

# Rendering the table with the fixed styling method
st.table(df.style.map(highlight_safe, subset=['Over Prob']))

# --- 4. LIVE BREAKDOWN ---
st.divider()
st.header("📉 Quarter-by-Quarter Risk Analysis")

selected_game = st.selectbox("Select game to analyze live:", df['Game'])
game_prob = df[df['Game'] == selected_game]['Over Prob'].values[0]

col1, col2 = st.columns([1, 2])

with col1:
    current_q = st.radio("Current Quarter Step:", [1, 2, 3, 4], horizontal=True)
    live_odds = st.number_input("Live Odds for this Quarter:", value=1.91)
    
    if 'cumulative_loss' not in st.session_state or current_q == 1:
        st.session_state.cumulative_loss = 0.0

with col2:
    q_left = 5 - current_q
    bust_risk = calculate_failure_risk(game_prob, q_left)
    
    st.subheader(f"Analysis for Q{current_q}")
    
    if current_q == 1:
        move = base_unit
    else:
        move = martingale_recovery(base_unit, st.session_state.cumulative_loss, live_odds)

    st.metric("Move Suggestion", f"{move} units")
    st.metric("Risk of losing all remaining Qs", f"{bust_risk}%")
    st.progress(1 - (bust_risk / 100))

# --- 5. LOGGING BUTTONS ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    if st.button("🔴 Log Loss for Current Quarter"):
        st.session_state.cumulative_loss += (move if current_q > 1 else base_unit)
        st.error(f"Total Loss: {st.session_state.cumulative_loss}. Move to next Quarter.")

with c2:
    if st.button("🟢 Log Win / Reset"):
        st.session_state.cumulative_loss = 0.0
        st.success("Strategy Successful. Resetting...")
