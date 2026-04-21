import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone, timedelta
from streamlit_option_menu import option_menu

# --- 1. CONFIG & STYLING ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576'
st.set_page_config(page_title="NBA Quant Engine", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a "Bloomberg Terminal" aesthetic
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    div[data-testid="stExpander"] { border: none; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. RISK MANAGEMENT LOGIC (The "Brain") ---
def calculate_risk_metrics(bankroll, target, current_loss, odds):
    if odds <= 1: return 0, 0
    next_stake = (current_loss + target) / (odds - 1)
    
    # Calculation: How many steps left before bankroll is depleted?
    steps_left = 0
    temp_bankroll = bankroll - current_loss
    running_loss = current_loss
    
    while temp_bankroll > next_stake:
        steps_left += 1
        running_loss += next_stake
        next_stake = (running_loss + target) / (odds - 1)
        temp_bankroll -= next_stake
        if steps_left > 10: break # Safety break
        
    return round(next_stake, 2), steps_left

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111532.png", width=50)
    st.title("QUANT OPS")
    
    selected = option_menu(
        menu_title=None,
        options=["Command", "Analytics", "Risk Engine", "Settings"],
        icons=["terminal", "graph-up", "shield-lock", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#0d1117"},
            "icon": {"color": "#58a6ff", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "color": "#c9d1d9"},
            "nav-link-selected": {"background-color": "#21262d"},
        }
    )

    st.divider()
    bankroll = st.number_input("💵 Total Bankroll ($)", value=1000.0)
    target_unit = st.number_input("🎯 Target Profit ($)", value=20.0)

# --- 4. DATA ENGINE ---
@st.cache_data(ttl=600)
def fetch_nba_data():
    # In a real app, you would also fetch team stats from an API like RapidAPI or NBA_API
    # For now, we enhance the Odds API data
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals"
    try:
        r = requests.get(url)
        return r.json()
    except:
        return []

# --- 5. PAGE ROUTING ---

if selected == "Command":
    st.header("🎮 Strategic Command Center")
    data = fetch_nba_data()
    
    col1, col2, col3 = st.columns(3)
    
    if data:
        for i, game in enumerate(data[:6]): # Show top 6 games as cards
            home = game['home_team']
            away = game['away_team']
            with [col1, col2, col3][i%3]:
                with st.container():
                    st.markdown(f"### {home} 🆚 {away}")
                    st.caption(f"Starts: {game['commence_time']}")
                    # Logic-based recommendation placeholder
                    st.info("💡 PREDICTION: High Pace Game - Lean OVER")
                    st.button(f"Analyze {home}", key=f"btn_{i}")

elif selected == "Risk Engine":
    st.header("🛡️ Martingale Risk Auditor")
    
    c1, c2 = st.columns(2)
    with c1:
        loss_seq = st.number_input("Current Sequential Loss ($)", value=0.0)
        curr_odds = st.slider("Market Odds", 1.5, 5.0, 1.91)
    
    stake, steps = calculate_risk_metrics(bankroll, target_unit, loss_seq, curr_odds)
    
    with c2:
        st.metric("Required Stake", f"${stake}", delta=f"{round((stake/bankroll)*100, 1)}% of Bank")
        st.metric("Survival Buffer", f"{steps} Steps", delta="Danger Zone" if steps < 3 else "Safe", delta_color="inverse")

    if steps < 2:
        st.error("🚨 CRITICAL RISK: Bankroll cannot support another doubling. Lower your Target Profit.")

elif selected == "Analytics":
    st.header("📊 Team Statistical Deep-Dive")
    st.markdown("---")
    # Here you would integrate a dataframe of team PPG (Points Per Game)
    mock_stats = pd.DataFrame({
        'Team': ['Lakers', 'Celtics', 'Nuggets', 'Suns'],
        'PPG': [118.5, 120.3, 114.9, 116.2],
        'Pace': [101.2, 99.5, 96.8, 100.1],
        'Over %': ['55%', '62%', '48%', '51%']
    })
    st.table(mock_stats)
