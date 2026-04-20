import streamlit as st
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="Pro Strategy Bot", layout="wide")
st.title("🛡️ NBA & Soccer Strategy Engine")

# 2. STATE MANAGEMENT
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- NEW: TODAY'S SCHEDULE DATA (April 20, 2026) ---
nba_games = [
    {"Game": "Cavaliers vs Raptors", "Time": "19:00 ET", "Status": "Game 2"},
    {"Game": "Knicks vs Hawks", "Time": "20:00 ET", "Status": "Game 2"},
    {"Game": "Nuggets vs T-Wolves", "Time": "22:30 ET", "Status": "Game 2"}
]

soccer_games = [
    {"Match": "Crystal Palace vs West Ham", "League": "Premier League", "Time": "20:00 BST"},
    {"Match": "Santos Laguna vs Atlas", "League": "Liga MX", "Status": "Finished (0-1)"}
]

# 3. SIDEBAR & SCHEDULE VIEWER
with st.sidebar:
    st.header("Settings")
    mode = st.radio("Select Sport", ["NBA", "Soccer"])
    base_bet = st.number_input("Base Bet ($)", value=25.0)
    
    current_bet = base_bet * (2 ** st.session_state.streak)
    st.divider()
    st.metric("NEXT BET", f"${current_bet:,.2f}")
    
    st.subheader("📅 Today's Schedule")
    if mode == "NBA":
        st.table(pd.DataFrame(nba_games))
    else:
        st.table(pd.DataFrame(soccer_games))
    
    if st.button("Reset Strategy"):
        st.session_state.streak = 0
        st.session_state.history = []
        st.rerun()

# 4. DYNAMIC TARGETING & INPUT
if mode == "NBA":
    target_label, default_line, alt_lines = "Points", 51.5, [48.5, 51.5, 54.5]
else:
    target_label, default_line, alt_lines = "Goals", 0.5, [0.5, 1.5]

col1, col2 = st.columns([2, 1])

with col1:
    with st.form("entry_form"):
        game = st.selectbox("Current Game", [g["Game"] if mode=="NBA" else g["Match"] for g in (nba_games if mode=="NBA" else soccer_games)])
        segment = st.selectbox("Segment", ["Q1", "Q2", "Q3", "Q4", "1st Half"])
        score = st.number_input(f"Actual {target_label}", min_value=0.0, step=0.5)
        target = st.selectbox("Target Line", alt_lines, index=1 if mode=="NBA" else 0)
        
        if st.form_submit_button("PROCESS"):
            win = score > target
            if win:
                st.balloons()
                st.success(f"🔥 WIN! Resetting to ${base_bet}.")
                st.session_state.streak = 0
            else:
                st.session_state.streak += 1
                st.error(f"❌ LOSS. Step {st.session_state.streak + 1}: Bet ${base_bet * (2**st.session_state.streak)}")
            
            st.session_state.history.append({
                "Game": game, "Seg": segment, "Score": score, "Result": "WIN" if win else "LOSS"
            })

with col2:
    st.subheader("Sequence History")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history).tail(8))
def calculate_bet(stake, odds, odds_type='decimal'):
    """
    Calculates the potential win and net profit.
    :param stake: The amount of money wagered.
    :param odds: The odds offered (Decimal or American).
    :param odds_type: 'decimal' or 'american'.
    """
    if odds_type == 'decimal':
        # Potential Win = Stake * Decimal Odds
        potential_win = stake * odds
    
    elif odds_type == 'american':
        if odds > 0:
            # Positive American odds (e.g., +150)
            potential_win = stake * (1 + (odds / 100))
        else:
            # Negative American odds (e.g., -110)
            potential_win = stake * (1 + (100 / abs(odds)))
    
    else:
        return "Unsupported odds type."

    net_profit = potential_win - stake
    
    return {
        "Stake": f"${stake:.2f}",
        "Potential Win (Total Payout)": f"${potential_win:.2f}",
        "Net Profit": f"${net_profit:.2f}"
    }

# Example usage:
# A $100 bet on odds of 2.50
result = calculate_bet(100, 2.50)
print(result)
