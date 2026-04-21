import streamlit as st

def calculate_martingale(initial_stake, current_step, odds):
    # Total loss is the sum of all previous stakes
    # For this simulation, we calculate the next stake needed to recover and profit
    # Formula: Stake = (Total Loss + Target Profit) / (Odds - 1)
    
    target_profit = initial_stake
    # Simple doubling logic or odds-adjusted logic
    if odds > 2.0:
        next_move = (initial_stake * (2 ** current_step)) / (odds - 1)
    else:
        next_move = initial_stake * (2 ** current_step)
        
    return round(next_move, 2)

st.set_page_config(page_title="NBA Quarter Martingale Analyzer", layout="centered")

st.title("🏀 NBA Quarter-by-Quarter Analyzer")
st.markdown("""
This tool analyzes the **Martingale Strategy** across the four quarters of an NBA game. 
Input the game data below to calculate the next logical move.
""")

with st.sidebar:
    st.header("Parameters")
    base_unit = st.number_input("Base Stake (Unit)", min_value=1.0, value=10.0)
    current_q = st.selectbox("Current Quarter", [1, 2, 3, 4])
    game_status = st.radio("Result of previous move:", ["Start of Game", "Won", "Lost"])

# Logic for Strategy Suggestions
if 'history' not in st.session_state:
    st.session_state.history = []

st.subheader(f"Analysis: Quarter {current_q}")

col1, col2 = st.columns(2)

with col1:
    live_odds = st.number_input("Live Odds for this Quarter", min_value=1.01, value=1.90)
    
with col2:
    if game_status == "Won":
        st.success("Strategy Reset. Start back at Quarter 1 with Base Unit.")
        suggestion = base_unit
    elif game_status == "Lost":
        # Calculate progression based on the quarter step
        suggestion = calculate_martingale(base_unit, current_q - 1, live_odds)
        st.warning(f"Next Logical Move: {suggestion} units")
    else:
        st.info(f"Initial Move: {base_unit} units")
        suggestion = base_unit

# Probability Analysis
st.divider()
st.subheader("Statistical Probability")
implied_prob = (1 / live_odds) * 100
st.write(f"Implied probability for this move: **{implied_prob:.2f}%**")

# Risk Warning
st.error("⚠️ **Risk Factor:** Martingale assumes infinite capital. In NBA, if all 4 quarters lose, the 'Table Max' or bankroll depletion is a significant risk.")

# Table for progression visualization
st.subheader("Progression Table (Typical 1.90 Odds)")
data = []
for i in range(1, 5):
    step_stake = round(base_unit * (2.1 ** (i-1)), 2) # Adjusted for standard juice
    data.append({"Quarter": i, "Estimated Stake": step_stake, "Total Risk": round(step_stake * i, 2)})

st.table(data)
