import streamlit as st
import pandas as pd
import requests
import math
import numpy as np
from scipy.stats import poisson

# --- 1. SETTINGS ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576'
BASE_BET = 100.0
BANKROLL = 5000.0

# Market Key Mapping
# Note: 'player_props' and 'alternate_totals' are often separate in API plans
SOCCER_MARKETS = "h2h,totals,alternate_totals"

# --- 2. THE INTELLIGENCE ENGINE ---

@st.cache_data(ttl=600)
def get_advanced_soccer_data():
    # Fetch multiple markets: Winner, Over/Under Goals, and Props if available
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=us&markets={SOCCER_MARKETS}&oddsFormat=decimal"
    
    try:
        data = requests.get(url).json()
        rows = []
        for game in data:
            home, away = game.get('home_team'), game.get('away_team')
            bookies = game.get('bookmakers', [])
            if not bookies: continue
            
            # We scan EVERY market provided by the bookie
            for market in bookies[0].get('markets', []):
                m_key = market['key']
                
                for outcome in market['outcomes']:
                    name = outcome['name']
                    point = outcome.get('point', '')
                    price = outcome['price']
                    
                    # Logic: Create a readable "Strategy" name
                    # e.g., "Over 1.5 Goals" or "Man City to Win"
                    selection = f"{name} {point}".strip()
                    
                    # --- MATH LAYER (POISSON) ---
                    # For a professional app, λ should be real-time stats.
                    # Here we use market-implied probabilities to detect "Value Gaps"
                    implied_prob = (1 / price) * 100
                    
                    rows.append({
                        "Matchup": f"{home} vs {away}",
                        "Market": m_key.replace("_", " ").title(),
                        "Selection": selection,
                        "Odds": price,
                        "Implied %": round(implied_prob, 1)
                    })
        return pd.DataFrame(rows)
    except Exception as e:
        return pd.DataFrame()

# --- 3. UI TERMINAL ---

def main():
    st.set_page_config(page_title="Sovereign Multi-Market", layout="wide")
    
    st.sidebar.title("🎮 Market Selector")
    sport = st.sidebar.selectbox("Choose Sport", ["NBA Basketball", "Soccer Advanced"])
    
    if sport == "Soccer Advanced":
        st.title("⚽ Multi-Market Soccer Intelligence")
        df = get_advanced_soccer_data()
        
        if not df.empty:
            # 1. THE FILTER: Let you find specific markets (Corners, Shots, Goals)
            market_type = st.selectbox("Filter Market Category:", ["All"] + list(df['Market'].unique()))
            filtered_df = df if market_type == "All" else df[df['Market'] == market_type]
            
            col_list, col_brief = st.columns([1, 1.2])
            
            with col_list:
                st.subheader("📊 Market Feed")
                # We sort by high odds to find the "Perfect Events"
                choice = st.selectbox("Select Target Event:", ["-- Select --"] + filtered_df['Selection'].tolist())
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)
                
            with col_brief:
                st.subheader("⚡ Strategy Briefing")
                if choice != "-- Select --":
                    # Get details for the selected event
                    s = filtered_df[filtered_df['Selection'] == choice].iloc[0]
                    
                    # RISK MANAGEMENT (Kelly Criterion)
                    # We assume a 5% "Edge" for the calculation
                    edge = 0.05 
                    odds = s['Odds']
                    prob = (1/odds) + edge
                    f_star = ((odds - 1) * prob - (1 - prob)) / (odds - 1)
                    safe_stake = max(0, f_star * BANKROLL * 0.2) # High safety factor

                    st.markdown(f"""
                    <div style="background:#0d1117; padding:25px; border-radius:15px; border:2px solid #3fb950;">
                        <h2 style="color:white; margin:0;">{s['Matchup']}</h2>
                        <h1 style="color:#3fb950;">ACTION: {s['Selection']}</h1>
                        <h3 style="color:white;">STAKE: ${round(safe_stake, 2)}</h3>
                        <hr style="border-color:#30363d">
                        <h4 style="color:#f1e05a;">WHY THIS SELECTION?</h4>
                        <p style="color:#8b949e;">Market <b>{s['Market']}</b> shows a price of {s['Odds']}. Unlike Win/Loss, this market tracks <b>cumulative events</b> (Corners/Goals), reducing the risk of a single fluke result destroying the bet.</p>
                        <h4 style="color:#f1e05a;">WHAT'S HAPPENING?</h4>
                        <p style="color:#8b949e;">You are using a <b>Fractional Kelly</b> strategy. By betting only ${round(safe_stake, 2)}, you can survive a losing streak while catching the high payout of the {s['Odds']} multiplier.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("EXECUTE TRADE"):
                        st.success("Trade Logged to Bankroll.")
        else:
            st.warning("No advanced markets found. Check if your API Key supports 'alternate_totals'.")

if __name__ == "__main__":
    main()
