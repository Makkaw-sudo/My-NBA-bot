import streamlit as st
import math

# --- CONFIGURATION (Change these to match your wallet) ---
BANKROLL = 5000.00
BASE_BET = 100.00
MAX_RISK_LIMIT = 0.15 # 15% of bankroll is the absolute "Danger" limit

# --- MATH ENGINE ---
def calculate_safety_and_profit(step, odds, line, expected):
    # Martingale Stake
    current_stake = BASE_BET * (2 ** step)
    
    # Total money spent so far in this game
    total_wagered = sum([BASE_BET * (2**i) for i in range(step + 1)])
    
    # Win Probability (Normal Distribution Approximation)
    std_dev = 4.5
    z_score = (line - expected) / std_dev
    prob = 0.5 * (1 + math.erf(-z_score / math.sqrt(2)))
    
    # Profit Calculation
    potential_return = current_stake * odds
    net_profit = potential_return - total_wagered
    
    # Danger Detection
    is_danger = total_wagered > (BANKROLL * MAX_RISK_LIMIT)
    
    return round(prob * 100, 1), current_stake, round(net_profit, 2), is_danger

# --- APP SETUP ---
st.set_page_config(page_title="NBA EDGE COMMAND", layout="centered")

if 'step' not in st.session_state: st.session_state.step = 0

# --- LIVE DATA (This represents your actual game leads) ---
# When you have a new game, you update these 4 values:
game_name = "Lakers vs Warriors"
expected_pts = 61.5
current_line = 54.5 # The line the bookie gives you
current_odds = 2.3  # The odds the bookie gives you

# Run Math
prob, stake, profit, danger = calculate_safety_and_profit(
    st.session_state.step, current_odds, current_line, expected_pts
)

# --- DISPLAY ---
st.title("🛡️ NBA Strategy Center")

# Danger Styling
status_color = "#ff7b72" if danger else "#3fb950"
bg_color = "rgba(255, 123, 114, 0.1)" if danger else "rgba(63, 185, 80, 0.05)"

st.markdown(f"""
    <div style="border: 2px solid {status_color}; background: {bg_color}; padding: 25px; border-radius: 15px; text-align: center;">
        <h2 style="color: white; margin-bottom: 5px;">{game_name}</h2>
        <p style="color: #8b949e; margin-bottom: 20px;">Martingale Step: {st.session_state.step + 1}</p>
        
        <div style="background: #0d1117; border: 1px dashed {status_color}; padding: 15px; border-radius: 10px;">
            <div style="color: #8b949e; font-size: 14px;">EXACT INSTRUCTION:</div>
            <div style="font-size: 28px; font-weight: bold; color: white;">
                BET <span style="color: {status_color};">OVER {current_line}</span>
            </div>
            <div style="color: #8b949e;">ODDS: {current_odds}</div>
        </div>

        <div style="display: flex; justify-content: space-around; margin-top: 20px;">
            <div>
                <small style="color: #8b949e;">WIN PROBABILITY</small>
                <div style="font-size: 24px; font-weight: bold; color: {status_color};">{prob}%</div>
            </div>
            <div>
                <small style="color: #8b949e;">REQUIRED STAKE</small>
                <div style="font-size: 24px; font-weight: bold; color: white;">${stake}</div>
            </div>
            <div>
                <small style="color: #8b949e;">NET PROFIT</small>
                <div style="font-size: 24px; font-weight: bold; color: #3fb950;">+${profit}</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- EMOTIONLESS BUTTONS ---
st.write("")
col1, col2 = st.columns(2)
with col1:
    if st.button("✅ WIN (Reset Stake)", use_container_width=True):
        st.session_state.step = 0
        st.rerun()
with col2:
    if st.button("❌ LOSS (Double Stake)", use_container_width=True):
        st.session_state.step += 1
        st.rerun()

if danger:
    st.error("🚨 STOP! Your bankroll is at high risk. Do not double again.")
