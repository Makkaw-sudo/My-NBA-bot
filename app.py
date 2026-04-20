import streamlit as st
import pandas as pd

# 1. Advanced Analysis Logic: Calculate probability based on Team A + Team B avg
def get_strategy_probability(team_a_avg, team_b_avg, target=51.5):
    combined_avg = team_a_avg + team_b_avg
    # Simple probability: If avg is 5 points over target, hit rate is ~85%
    diff = combined_avg - target
    base_prob = 50.0
    probability = base_prob + (diff * 5)
    return min(max(probability, 10.0), 99.0) # Cap between 10% and 99%

st.title("🏀 Pro Analysis: Daily Game Hub")

# --- DAILY GAME ANALYSIS ---
st.header("📋 Today's Game Predictions")
# Example Data: In a full app, this would fetch from an API
games = [
    {"Match": "Cavaliers vs Raptors", "Q1 Avg": 58.9, "Q4 Avg": 54.2},
    {"Match": "Nuggets vs Timberwolves", "Q1 Avg": 59.9, "Q4 Avg": 49.8},
    {"Match": "Knicks vs Hawks", "Q1 Avg": 60.0, "Q4 Avg": 51.1}
]

selected_game = st.selectbox("Select Game for Analysis", [g["Match"] for g in games])
selected_q = st.radio("Target Quarter", ["1st Quarter", "4th Quarter"])

# Dynamic Analysis Output
game_info = next(g for g in games if g["Match"] == selected_game)
q_stat = game_info["Q1 Avg"] if selected_q == "1st Quarter" else game_info["Q4 Avg"]
hit_prob = get_strategy_probability(q_stat/2, q_stat/2) # Simplified for example

st.metric(label=f"Probability to hit Over 51.5 in {selected_q}", value=f"{hit_prob:.1f}%")

if hit_prob > 70:
    st.success("🔥 High Probability Matchup")
elif hit_prob > 50:
    st.warning("⚠️ Moderate Risk - Watch Live")
else:
    st.error("❄️ Low Probability - Skip this Quarter")

# --- MULTI-GAME STRATEGY TRACKER ---
st.divider()
st.subheader("🔄 Live Strategy & Risk Alerts")

if 'consecutive_losses' not in st.session_state:
    st.session_state.consecutive_losses = 0
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0

# Alert System
if st.session_state.consecutive_losses >= 3:
    st.error(f"🚨 CRITICAL ALERT: {st.session_state.consecutive_losses} consecutive losses. Next stake is very high!")
elif st.session_state.consecutive_losses > 0:
    st.info(f"⚡ Recovery Mode: Moving to Level {st.session_state.consecutive_losses + 1}")

base_bet = st.number_input("Base Bet ($)", value=10.0)
current_stake = base_bet * (2 ** st.session_state.consecutive_losses)

st.write(f"### Current Stake: **${current_stake:.2f}**")

# Interaction
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("✅ WIN"):
        st.session_state.bankroll += current_stake
        st.session_state.consecutive_losses = 0
        st.balloons()
with c2:
    if st.button("❌ LOSE"):
        st.session_state.bankroll -= current_stake
        st.session_state.consecutive_losses += 1
with c3:
    if st.button("Reset"):
        st.session_state.consecutive_losses = 0

# --- SIMPLE BREAKDOWN ---
st.divider()
with st.expander("📝 Strategy Breakdown"):
    st.write(f"""
    1. **The Goal:** Hit a single win within a game sequence.
    2. **The Math:** If a quarter misses, we double the stake (${current_stake} ➔ ${current_stake*2}).
    3. **The Risk:** Your current streak is {st.session_state.consecutive_losses} losses.
    4. **Recommendation:** Only play games with >65% probability for the chosen quarter.
    """)
