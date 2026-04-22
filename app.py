import streamlit as st
import math

# --- 1. CONFIGURATION ---
BANKROLL = 5000.00  # Total money you have for betting
MAX_RISK_PCT = 0.05 # Never risk more than 5% of bankroll in one series
BASE_UNIT = 100.00  # Your starting bet size

# --- 2. SAFETY & PROFIT CALCULATOR ---
def get_safe_instruction(step, odds, target_line):
    # Calculate Martingale progression
    current_stake = BASE_UNIT * (2 ** step)
    
    # Calculate DANGER LEVEL
    total_at_stake = sum([BASE_UNIT * (2**i) for i in range(step + 1)])
    is_dangerous = total_at_stake > (BANKROLL * MAX_RISK_PCT)
    
    # Profit Math
    potential_return = current_stake * odds
    net_profit = potential_return - total_at_stake
    
    return {
        "stake": current_stake,
        "net_profit": net_profit,
        "danger": is_dangerous,
        "total_at_stake": total_at_stake
    }

# --- 3. SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 0

# --- 4. STYLE ---
st.markdown("""
    <style>
    .safety-box { padding: 20px; border-radius: 12px; border: 2px solid; margin-bottom: 20px; text-align: center; }
    .safe { border-color: #3fb950; background: rgba(63, 185, 80, 0.05); }
    .danger { border-color: #ff7b72; background: rgba(255, 123, 114, 0.1); animation: blink 1s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    .big-value { font-size: 32px; font-weight: bold; display: block; }
    </style>
""", unsafe_allow_html=True)

# --- 5. DASHBOARD ---
st.title("🛡️ Risk-Adjusted Betting Command")

# Inputs (These would come from your live API/Scraper)
current_game = "Lakers vs Warriors"
current_target = 54.5
current_odds = 2.3  # Example high odds

# Get logic results
data = get_safe_instruction(st.session_state.step, current_odds, current_target)

# Display Danger Warning if risk is too high
status_class = "danger" if data['danger'] else "safe"
status_text = "⚠️ HIGH RISK - REDUCE STAKE" if data['danger'] else "✅ SAFE MARGIN"

st.markdown(f"""
    <div class="safety-box {status_class}">
        <small style="color: #8b949e;">{status_text}</small>
        <div style="margin: 10px 0;">
            <span style="color: #8b949e;">BET OVER:</span>
            <span class="big-value" style="color: white;">{current_target} @ {current_odds}</span>
        </div>
        <div style="display: flex; justify-content: space-around;">
            <div>
                <small style="color: #8b949e;">SUGGESTED STAKE</small>
                <div style="font-size: 24px; color: #ff7b72; font-weight: bold;">${data['stake']}</div>
            </div>
            <div>
                <small style="color: #8b949e;">NET PROFIT</small>
                <div style="font-size: 24px; color: #3fb950; font-weight: bold;">+${data['net_profit']:.2f}</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 6. EMOTIONLESS CONTROLS ---
st.write(f"**Series Exposure:** ${data['total_at_stake']} / ${BANKROLL}")

col1, col2 = st.columns(2)
with col1:
    if st.button("✅ WIN (Restart)", use_container_width=True):
        st.session_state.step = 0
        st.rerun()
with col2:
    if st.button("❌ LOSS (Next Step)", use_container_width=True):
        st.session_state.step += 1
        st.rerun()

if st.button("Emergency Reset"):
    st.session_state.step = 0
    st.rerun()
