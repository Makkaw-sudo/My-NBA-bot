import streamlit as st
import pandas as pd
import random

# --- CONFIG & STYLING ---
st.set_page_config(page_title="NBA Analytics & Martingale", layout="wide")

# --- MOCK DATA FOR DAILY GAMES ---
# In a production app, you would fetch this from an API like Sportsradar or API-NBA
def get_daily_games():
    teams = ["Celtics", "Lakers", "Warriors", "Nuggets", "Bucks", "Suns", "Knicks", "76ers"]
    games = []
    for i in range(len(teams)//2):
        home = teams[i]
        away = teams[-(i+1)]
        # Simulated probability logic based on average scoring
        prob = round(random.uniform(51.0, 58.5), 1) 
        line = 55.5  # Standard quarter over/under line
        odds = 1.91  # Standard juice
        games.append({"Match": f"{home} vs {away}", "Market": f"Over {line}", "Probability": f"{prob}%", "Odds": odds})
    return games

# --- CALCULATION LOGIC ---
def calculate_next_move(initial_stake, current_loss, odds):
    # Martingale formula: (Total Loss + Target Profit) / (Odds - 1)
    target_profit = initial_stake
    needed = (current_loss + target_profit) / (odds - 1)
    return round(needed, 2)

# --- APP TABS ---
tab1, tab2 = st.tabs(["📊 Daily Game Analysis", "📈 Martingale Calculator"])

# --- TAB 1: MAIN PAGE (DAILY GAMES) ---
with tab1:
    st.header("Daily NBA 'Safe Over' Predictions")
    st.write("Analysis of games with a high statistical probability of hitting **Over 55.5** in at least one quarter.")
    
    daily_data = get_daily_games()
    df = pd.DataFrame(daily_data)
    
    # Visualizing the table
    st.table(df)
    
    st.info("💡 **Strategy Tip:** Look for games with >55% probability to start your Martingale sequence.")

# --- TAB 2: QUARTER-BY-QUARTER ANALYZER ---
with tab2:
    st.header("Martingale Progression Analyzer")
    st.write("Use this to calculate your move if the previous quarter lost.")

    col1, col2 = st.columns(2)
    
    with col1:
        base_bet = st.number_input("Starting Stake (Unit)", min_value=1.0, value=10.0)
        q_step = st.radio("Select Current Step:", [1, 2, 3, 4], 
                          help="Which quarter of the game are you analyzing?")
        current_odds = st.number_input("Current Live Odds", min_value=1.01, value=1.91)

    # Track losses through session state to suggest the next move
    if 'total_lost' not in st.session_state:
        st.session_state.total_lost = 0.0

    with col2:
        st.subheader("Action Suggestion")
        
        if q_step == 1:
            st.session_state.total_lost = 0.0
            st.success(f"**Move 1:** Stake **{base_bet}**")
            st.caption("Starting fresh for Q1.")
        else:
            # Simple calculation based on previous steps
            # For Q2, we assume Q1 lost. For Q3, we assume Q1+Q2 lost.
            prev_losses = base_bet * (2.1 ** (q_step - 2)) # Estimated progression
            suggestion = calculate_next_move(base_bet, prev_losses, current_odds)
            
            st.warning(f"**Move {q_step}:** Stake **{suggestion}**")
            st.write(f"Total capital at risk if this loses: {round(prev_losses + suggestion, 2)}")

    st.divider()
    st.subheader("Probability of a 'Total Loss' (0/4 Quarters)")
    # If prob of winning one Q is 55%, prob of losing all 4 is (0.45)^4
    fail_rate = (0.45 ** 4) * 100
    st.write(f"Based on a 55% win rate per quarter, the chance of losing all 4 quarters is approximately **{fail_rate:.2f}%**.")

# --- FOOTER ---
st.markdown("---")
st.caption("⚠️ This app is for analytical purposes only. Martingale carries high risk of bankroll depletion.")
