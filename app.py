import streamlit as st
import pandas as pd

st.title("Martingale Strategy Dashboard")

# 1. Setup Session State for persistent data
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_bet' not in st.session_state:
    st.session_state.current_bet = 10.0  # Default base bet

# 2. Sidebar Inputs
st.sidebar.header("Settings")
base_bet = st.sidebar.number_input("Base Bet Amount", value=10.0)
target_profit = st.sidebar.number_input("Target Profit", value=100.0)

# 3. Betting Controls
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✅ Win"):
        st.session_state.history.append({"Result": "Win", "Stake": st.session_state.current_bet})
        st.session_state.current_bet = base_bet  # Reset on win

with col2:
    if st.button("❌ Loss"):
        st.session_state.history.append({"Result": "Loss", "Stake": st.session_state.current_bet})
        st.session_state.current_bet *= 2  # Double on loss

with col3:
    if st.button("Reset Session"):
        st.session_state.history = []
        st.session_state.current_bet = base_bet

# 4. Data Processing
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    
    # Simple profit calculation (assuming 2.00 decimal odds for Martingale)
    df['Profit/Loss'] = df.apply(lambda x: x['Stake'] if x['Result'] == 'Win' else -x['Stake'], axis=1)
    df['Cumulative Profit'] = df['Profit/Loss'].cumsum()

    # 5. Display Stats
    st.metric("Next Recommended Bet", f"${st.session_state.current_bet}")
    st.metric("Total Profit/Loss", f"${df['Cumulative Profit'].iloc[-1]}")

    # 6. Performance Chart
    st.line_chart(df['Cumulative Profit'])
    st.table(df)
else:
    st.info("Start by logging your first bet result.")
