import streamlit as st
import pandas as pd
import numpy as np

# --- 1. PROBABILITY LOGIC ---
def calculate_failure_risk(prob_win_per_q, quarters_left):
    """Calculates the chance of losing all remaining quarters."""
    prob_loss_per_q = 1 - (prob_win_per_q / 100)
    return round((prob_loss_per_q ** quarters_left) * 100, 2)

def martingale_recovery(initial_stake, total_loss, odds):
    """Calculates stake needed to recover all losses plus original profit."""
    return round((total_loss + initial_stake) / (odds - 1), 2)

# --- 2. APP UI SETUP ---
st.set_page_config(page_title="NBA Quarter Martingale Pro", layout="wide")
st.title("🏀 NBA Game & Martingale Analyzer")

# Sidebar for Global Settings
with st.sidebar:
    st.header("Strategy Settings")
    base_unit = st.number_input("Base Unit Stake", min_value=1.0, value=10.0)
    target_over = 55.5
    st.info(f"Targeting Over {target_over} points per quarter.")

# --- 3. MAIN PAGE: DAILY GAMES ---
st.header("📅 Daily Game Analysis")
# Simulated data - in production, fetch from NBA-API or Sportradar
daily_games = [
    {"Game": "Celtics @ 76ers", "Over Prob": 58.2, "Odds": 1.88, "Status": "Upcoming"},
    {"Game": "Suns @ OKC", "Over Prob": 55.5, "Odds": 1.91, "Status": "Upcoming"},
    {"Game": "Lakers @ Rockets", "Over Prob": 52.1, "Odds": 1.95, "Status": "Starting Soon"},
]

df = pd.DataFrame(daily_games)
# Highlighting 'Safe' games (above 55%)
def highlight_safe(val):
    color = 'lightgreen' if isinstance(val, float) and val >= 55.0 else 'white'
    return f'background-color: {color}'

st.table(df.style.applymap(highlight_safe, subset=['Over Prob']))

# --- 4. LIVE BREAKDOWN: QUARTER BY QUARTER ---
st.divider()
st.header("📉 Quarter-by-Quarter Risk Analysis")

# Select a game to analyze
selected_game = st.selectbox("Select game to analyze live:", df['Game'])
game_prob = df[df['Game'] == selected_game]['Over Prob'].values[0]

col1, col2 = st.columns([1, 2])

with col1:
    current_q = st.radio("Current Quarter Step:", [1, 2, 3, 4], horizontal=True)
    live_odds = st.number_input("Live Odds for this Quarter:", value=1.91)
    
    # Session state to track cumulative loss
    if 'cumulative_loss' not in st.session_state or current_q == 1:
        st.session_state.cumulative_loss = 0.0

with col2:
    q_left = 5 - current_q
    bust_risk = calculate_failure_risk(game_prob, q_left)
    
    st.subheader(f"Analysis for Q{current_q}")
    
    if current_q == 1:
        move = base_unit
        st.info(f"👉 **Next Move:** Stake **{move}**")
    else:
        # Assuming previous quarter was a loss to suggest the next logical move
        move = martingale_recovery(base_unit, st.session_state.cumulative_loss, live_odds)
        st.warning(f"👉 **Next Logical Move:** Stake **{move}** to recover previous losses.")

    st.metric("Probability of 'Busting' (Losing all remaining Qs)", f"{bust_risk}%")
    
    # Progress Bar for Risk
    st.progress(1 - (bust_risk / 100))
    st.caption("Lower bar means higher risk of losing the entire sequence.")

# --- 5. LOGIC FOR USER TO LOG LOSSES ---
st.divider()
if st.button("🔴 Log Loss for Current Quarter"):
    # Mocking the math: if user lost, they need to know what they've lost so far
    if current_q == 1:
        st.session_state.cumulative_loss = base_unit
    else:
        st.session_state.cumulative_loss += move
    st.error(f"Total Loss so far: {st.session_state.cumulative_loss}. Advance to Q{current_q + 1} for recovery move.")

if st.button("🟢 Log Win / Reset"):
    st.session_state.cumulative_loss = 0.0
    st.success("Strategy Successful. Reset to Q1.")
