import streamlit as st
import pandas as pd
import requests
import math

# --- 1. CORE ENGINE CONFIG ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576'
BANKROLL = 5000.0
BASE_BET = 100.0
HISTORICAL_AVG_Q = 57.5  # The "Smart" baseline for a standard NBA quarter
STD_DEV = 4.5           # Mathematical volatility constant

# --- 2. AUTOMATED DECISION LOGIC ---
def get_smart_leads():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals_q1,totals_q2&oddsFormat=decimal"
    try:
        data = requests.get(url).json()
        all_opportunities = []
        for game in data:
            bookie = game['bookmakers'][0] if game['bookmakers'] else None
            if bookie:
                m = bookie['markets'][0]
                line = m['outcomes'][0]['point']
                odds = m['outcomes'][0]['price']
                
                # MATHEMATICAL EDGE CALCULATION
                # We calculate how far the bookie line is from the "True Average"
                z_score = (line - HISTORICAL_AVG_Q) / STD_DEV
                prob = 0.5 * (1 + math.erf(-z_score / math.sqrt(2)))
                
                all_opportunities.append({
                    "Game": f"{game['home_team']} vs {game['away_team']}",
                    "Line": line,
                    "Odds": odds,
                    "Prob": round(prob * 100, 1),
                    "Edge": round(HISTORICAL_AVG_Q - line, 1)
                })
        
        # SORT BY HIGHEST PROBABILITY (The "Smart" Selection)
        df = pd.DataFrame(all_opportunities)
        return df.sort_values(by="Prob", ascending=False)
    except:
        return pd.DataFrame()

# --- 3. UI & RISK MANAGEMENT ---
st.set_page_config(page_title="Sovereign Intelligence", layout="wide")
if 'step' not in st.session_state: st.session_state.step = 0

st.title("🤖 Sovereign Autonomous Terminal")

# --- 4. EXECUTION ---
df_leads = get_smart_leads()

if not df_leads.empty:
    # AUTO-SELECT THE TOP PICK
    top_pick = df_leads.iloc[0]
    
    # Martingale Risk Management
    current_stake = BASE_BET * (2 ** st.session_state.step)
    
    # UI DISPLAY
    st.markdown(f"""
        <div style="background: #0d1117; padding: 40px; border-radius: 20px; border: 2px solid #58a6ff; box-shadow: 0px 0px 20px #58a6ff33;">
            <h3 style="color: #8b949e; margin:0;">PRIMARY SIGNAL IDENTIFIED</h3>
            <h1 style="font-size: 4em; margin: 10px 0;">{top_pick['Game']}</h1>
            
            <div style="background: #161b22; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <p style="color: #8b949e; margin:0;">MATHEMATICAL INSTRUCTION</p>
                <h2 style="font-size: 3em; color: white;">BET <span style="color: #3fb950;">OVER {top_pick['Line']}</span></h2>
            </div>
            
            <div style="display: flex; justify-content: space-between; text-align: center;">
                <div><p style="color: #8b949e;">WIN PROBABILITY</p><h2 style="color: #3fb950;">{top_pick['Prob']}%</h2></div>
                <div><p style="color: #8b949e;">REQUIRED STAKE</p><h2>${current_stake}</h2></div>
                <div><p style="color: #8b949e;">SYSTEM STEP</p><h2>{st.session_state.step + 1}</h2></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("✅ SIGNAL SUCCESS (RESET)", use_container_width=True):
            st.session_state.step = 0
            st.balloons()
            st.rerun()
    with c2:
        if st.button("❌ SIGNAL FAILED (RECOVER)", use_container_width=True):
            st.session_state.step += 1
            st.rerun()
    with c3:
        with st.expander("🔍 View Alternative High-Probability Leads"):
            st.table(df_leads.drop(columns=['Edge']))

else:
    st.info("Searching for a mathematical edge in live markets... Please wait.")
    if st.button("🔄 Force Scan"): st.rerun()

st.caption("Intelligence Engine: Martingale-Z Recovery Protocol")
