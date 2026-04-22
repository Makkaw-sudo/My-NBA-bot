import streamlit as st
import pandas as pd
import requests
import math

# --- 1. DYNAMIC DATA (2026 Live Averages) ---
# PPG divided by 4 to get Quarter Averages (Example data based on current season)
TEAM_STATS = {
    "Denver Nuggets": 30.5, "Boston Celtics": 28.7, "Cleveland Cavaliers": 29.8,
    "San Antonio Spurs": 29.9, "Oklahoma City Thunder": 29.7, "Miami Heat": 30.2,
    "Detroit Pistons": 29.4, "New York Knicks": 29.1, "Golden State Warriors": 28.6,
    "Sacramento Kings": 27.7, "Milwaukee Bucks": 27.6, "Brooklyn Nets": 26.5
}
DEFAULT_AVG = 28.5  # Fallback if team not in list
STD_DEV = 4.2       # Volatility constant

API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576'
BASE_BET = 100.0

# --- 2. ENHANCED LOGIC ---
def get_smart_leads():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals_q1&oddsFormat=decimal"
    try:
        data = requests.get(url).json()
        all_opportunities = []
        for game in data:
            home = game['home_team']
            away = game['away_team']
            
            # CALCULATE DYNAMIC MEAN FOR THIS SPECIFIC MATCHUP
            h_avg = TEAM_STATS.get(home, DEFAULT_AVG)
            a_avg = TEAM_STATS.get(away, DEFAULT_AVG)
            dynamic_mean = (h_avg + a_avg) / 2 
            
            bookie = game['bookmakers'][0] if game['bookmakers'] else None
            if bookie:
                market = bookie['markets'][0]
                line = market['outcomes'][0]['point']
                
                # Z-Score using the DYNAMIC MEAN instead of a flat 57.5
                z_score = (line - dynamic_mean) / STD_DEV
                prob = 0.5 * (1 + math.erf(-z_score / math.sqrt(2)))
                
                all_opportunities.append({
                    "Matchup": f"{home} vs {away}",
                    "Line": line,
                    "Exp Score": round(dynamic_mean, 1),
                    "Prob": round(prob * 100, 1),
                    "Edge": round(dynamic_mean - line, 2)
                })
        
        df = pd.DataFrame(all_opportunities)
        return df.sort_values(by="Prob", ascending=False)
    except Exception as e:
        st.error(f"API Connection Error: {e}")
        return pd.DataFrame()

# --- 3. UI OVERHAUL ---
st.set_page_config(page_title="Sovereign Intel v2", layout="wide")
if 'step' not in st.session_state: st.session_state.step = 0

st.title("🤖 Sovereign Terminal: Dynamic Engine")

df_leads = get_smart_leads()

if not df_leads.empty:
    top_pick = df_leads.iloc[0]
    current_stake = BASE_BET * (2 ** st.session_state.step)
    
    # Visual Feedback
    st.success(f"Target Acquired: {top_pick['Matchup']}")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric("Instruction", f"OVER {top_pick['Line']}", f"Edge: {top_pick['Edge']} pts")
        st.progress(top_pick['Prob'] / 100)
    with col2:
        st.metric("Required Stake", f"${current_stake}", f"Step {st.session_state.step + 1}")

    if st.button("EXECUTE SIGNAL"):
        st.info("System locked. Awaiting outcome...")
        
    st.divider()
    st.subheader("Alternative Mathematical Leads")
    st.dataframe(df_leads, use_container_width=True)
else:
    st.warning("No high-probability edges found in current market cycles.")
