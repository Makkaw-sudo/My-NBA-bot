import streamlit as st
import numpy as np
from scipy.stats import poisson

# --- 1. PROBABILITY MATH ENGINE ---
def calculate_poisson_probability(projected_total, bookie_line):
    """
    Uses Poisson Distribution to find the probability of a total 
    going OVER the bookie's line.
    """
    # Probability of being AT or BELOW the line
    prob_under = poisson.cdf(bookie_line, projected_total)
    prob_over = 1 - prob_under
    return round(prob_over * 100, 2)

# --- 2. MARTINGALE RISK AUDITOR ---
def calculate_martingale_exposure(stake, steps, odds):
    """Calculates total capital at risk if a streak continues."""
    total_risk = 0
    current_stake = stake
    for _ in range(steps):
        total_risk += current_stake
        current_stake = (total_risk + stake) / (odds - 1)
    return round(total_risk, 2)

# --- 3. THE ADVANCED UI ---
st.title("🎲 Martingale Probability Matrix")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📡 Live Analytics")
    current_q_avg = st.number_input("Historical Q-Avg (Points)", value=55.0)
    live_q_line = st.number_input("Current Live Line", value=58.5)
    
    # Calculate Probability
    win_prob = calculate_poisson_probability(current_q_avg, live_q_line)
    
    st.metric("Win Probability (Under)", f"{100 - win_prob}%", 
              delta=f"{round((100-win_prob)-50, 1)}% Edge vs Coin Flip")

with col2:
    st.subheader("💰 Martingale Recovery")
    starting_bet = st.number_input("Base Unit ($)", value=10.0)
    max_steps = st.slider("Max Survival Steps", 1, 8, 4)
    odds_decimal = st.number_input("Live Odds (Decimal)", value=1.91)
    
    exposure = calculate_martingale_exposure(starting_bet, max_steps, odds_decimal)
    
    st.warning(f"Total Capital Risked for {max_steps} steps: **${exposure}**")

# --- 4. THE LOGICAL DECISION MATRIX ---
st.divider()
st.subheader("🧠 Decision Intelligence")

# This is the "Advanced" part: Combining Win Prob with Martingale
if (100 - win_prob) > 55.0:
    st.success("🔥 STRATEGIC ENTRY: Win probability is high. Start Martingale Sequence.")
elif (100 - win_prob) < 45.0:
    st.error("🚫 HIGH RISK: Probability is against you. Skip this quarter.")
else:
    st.info("⚖️ COIN FLIP: Probability is ~50%. Wait for a better Lead.")
