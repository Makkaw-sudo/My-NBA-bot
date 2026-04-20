import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="NBA 4th Quarter Analysis", page_icon="🏀")

st.title("🏀 NBA 4th Quarter Betting Strategy")

# --- STRATEGY ANALYSIS SECTION ---
st.header("📊 Team Analysis (4th Quarter)")
st.info("Strategy: Over 51.5 Total Points in Q4")

# Simulated Team Data - In a real app, you'd fetch this from an API
team_data = {
    "Team": ["Lakers", "Celtics", "Warriors", "Nuggets", "Suns"],
    "Avg Q4 Points": [54.2, 51.1, 56.5, 49.8, 53.0],
    "Hit Rate (Over 51.5)": ["72%", "48%", "81%", "42%", "65%"],
    "Trend": ["🔥 Up", "❄️ Down", "🔥 Up", "➖ Stable", "🔥 Up"]
}
analysis_df = pd.DataFrame(team_data)

# Display Analysis Table
st.table(analysis_df)

# --- BETTING CALCULATOR WITH 4Q ICONS ---
st.divider()
st.subheader("⏱️ Live Session Tracker: Q4")

if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_stake' not in st.session_state:
    st.session_state.current_stake = 10.0

col1, col2 = st.columns(2)

with col1:
    base_bet = st.number_input("Base Stake ($)", value=10.0)
    target_q4_total = 51.5
    st.caption(f"Strategy Target: {target_q4_total} Points")

# --- ACTION BUTTONS ---
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("✅ Q4 HIT"):
        st.session_state.history.append({
            "Period": "4th Qtr",
            "Result": "WIN",
            "Stake": st.session_state.current_stake,
            "Icon": "💰"
        })
        st.session_state.current_stake = base_bet

with c2:
    if st.button("❌ Q4 MISS"):
        st.session_state.history.append({
            "Period": "4th Qtr",
            "Result": "LOSS",
            "Stake": st.session_state.current_stake,
            "Icon": "📉"
        })
        st.session_state.current_stake *= 2 # Martingale doubling logic

with c3:
    if st.button("🗑️ Clear"):
        st.session_state.history = []
        st.session_state.current_stake = base_bet

# --- RESULTS & PERCENTAGES ---
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    
    total_bets = len(df)
    wins = len(df[df['Result'] == 'WIN'])
    win_percentage = (wins / total_bets) * 100

    # Display Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Next Bet", f"${st.session_state.current_stake:.2f}")
    m2.metric("Win Rate", f"{win_percentage:.1f}%")
    m3.metric("Total Bets", total_bets)

    st.write("### 📝 Recent Session History")
    st.dataframe(df)
else:
    st.write("No active bets in this session. Select 'HIT' or 'MISS' to begin.")
