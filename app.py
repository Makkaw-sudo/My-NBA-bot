import streamlit as st
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="Pro Strategy Bot", layout="wide")
st.title("🛡️ NBA & Soccer Strategy Engine")

# 2. STATE MANAGEMENT (Carries loss streak across games)
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. SIDEBAR RISK CONTROL
with st.sidebar:
    st.header("Settings")
    mode = st.radio("Select Sport", ["NBA", "Soccer"])
    base_bet = st.number_input("Base Bet ($)", value=25.0)
    
    # Calculate current bet based on streak
    current_bet = base_bet * (2 ** st.session_state.streak)
    
    st.divider()
    st.metric("NEXT BET", f"${current_bet:,.2f}")
    st.write(f"Current Progression: Step {st.session_state.streak + 1}")
    
    if st.button("Reset Strategy (Full Reset)"):
        st.session_state.streak = 0
        st.session_state.history = []
        st.rerun()

# 4. DYNAMIC TARGETING
if mode == "NBA":
    target_label = "Quarter Points"
    default_line = 51.5
    alt_lines = [48.5, 51.5, 54.5]
    danger_msg = "Note: Playoff defenses can slow pace. Consider 48.5 for Knicks/Celtics."
else:
    target_label = "1st Half Goals"
    default_line = 0.5
    alt_lines = [0.5, 1.5]
    danger_msg = "Note: Look for German Bundesliga for high 0.5 FHG probability."

# 5. INPUT & ALERT SYSTEM
col1, col2 = st.columns([2, 1])

with col1:
    st.info(danger_msg)
    with st.form("entry_form"):
        game = st.text_input("Game Name")
        segment = st.selectbox("Segment", ["Q1", "Q2", "Q3", "Q4", "1st Half"])
        score = st.number_input(f"Actual {target_label}", min_value=0.0, step=0.5)
        target = st.selectbox("Your Target Line", alt_lines, index=1 if mode=="NBA" else 0)
        
        if st.form_submit_button("PROCESS"):
            win = score > target
            if win:
                st.balloons()
                st.success(f"🔥 WIN! {score} scored. Resetting bet to ${base_bet}.")
                st.session_state.streak = 0
            else:
                st.session_state.streak += 1
                st.error(f"❌ LOSS. Next bet doubled to ${base_bet * (2**st.session_state.streak)}")
            
            st.session_state.history.append({
                "Sport": mode, "Game": game, "Seg": segment, 
                "Score": score, "Target": target, "Result": "WIN" if win else "LOSS"
            })

with col2:
    st.subheader("Sequence History")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.table(df.tail(8)) # Show the 8-quarter sequence

# 6. WIN/LOSS PROBABILITY
st.divider()
st.subheader("Real-Time Analytics")
if st.session_state.history:
    total = len(st.session_state.history)
    wins = sum(1 for x in st.session_state.history if x['Result'] == "WIN")
    st.write(f"Session Success Rate: **{(wins/total)*100:.1f}%**")
