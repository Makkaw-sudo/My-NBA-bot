import streamlit as st

# --- ANALYSIS ENGINE ---
def get_bet_instruction(home_team, away_team, quarter, live_line, step, base_unit, odds=1.91):
    # 1. Calculate Martingale Stake
    # Stake = (Previous Losses + Target) / (Odds - 1)
    # For a simple doubling sequence:
    total_lost = sum([base_unit * (2**i) for i in range(step - 1)])
    stake = round((total_lost + base_unit) / (odds - 1), 2)

    # 2. Mock Analysis (In the real app, this pulls from your Team Data)
    # Let's assume the projected total for these teams is 55.0
    projected_avg = 55.0 
    
    # 3. Determine Direction
    if live_line < projected_avg:
        direction = "OVER"
    else:
        direction = "UNDER"

    # 4. THE COMMAND LINE
    instruction = f"Hey, bet **${stake}** on **{quarter} Quarter {direction} {live_line} points**."
    return instruction

# --- UI DISPLAY ---
st.title("🎯 NBA Betting Commander")

# User Inputs
col1, col2 = st.columns(2)
with col1:
    h_team = st.text_input("Home Team", "Lakers")
    q_target = st.selectbox("Target Quarter", ["1st", "2nd", "3rd", "4th"])
    m_step = st.number_input("Martingale Step", min_value=1, value=1)

with col2:
    a_team = st.text_input("Away Team", "Celtics")
    b_line = st.number_input("Bookie Line", value=52.5)
    unit = st.number_input("Base Unit ($)", value=10.0)

st.divider()

# Trigger the Command
command = get_bet_instruction(h_team, a_team, q_target, b_line, m_step, unit)

# High-Visibility Output
st.markdown(f"""
<div style="background-color:#1e2329; padding:20px; border-radius:15px; border: 2px solid #58a6ff; text-align:center;">
    <h2 style="color:white; margin:0;">{command}</h2>
</div>
""", unsafe_allow_html=True)
