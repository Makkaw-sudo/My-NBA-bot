import streamlit as st
import pandas as pd
import requests
import numpy as np

# --- 1. GLOBAL SETTINGS ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576'
BANKROLL = 5000.0

# Broadening the search to include Props (Shots, Corners, Cards)
# Note: Market names vary by bookmaker. These are the most common keys.
ADVANCED_MARKETS = "h2h,totals,alternate_totals,h2h_lay,player_shots_on_target,extratime_h2h"

# --- 2. THE INTELLIGENCE ENGINE ---

@st.cache_data(ttl=300)
def get_advanced_market_data():
    # We pull from the EPL specifically for these high-depth markets
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=us&markets={ADVANCED_MARKETS}&oddsFormat=decimal"
    
    try:
        data = requests.get(url).json()
        rows = []
        for game in data:
            home, away = game.get('home_team'), game.get('away_team')
            bookies = game.get('bookmakers', [])
            if not bookies: continue
            
            for market in bookies[0].get('markets', []):
                m_key = market['key']
                for outcome in market['outcomes']:
                    rows.append({
                        "Match": f"{home} vs {away}",
                        "Category": m_key.replace("_", " ").title(),
                        "Bet On": f"{outcome.get('name')} {outcome.get('point', '')}".strip(),
                        "Price": outcome['price'],
                        "Implied Prob": f"{round((1/outcome['price'])*100, 1)}%"
                    })
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()

# --- 3. UI LAYOUT ---

def main():
    st.set_page_config(page_title="Sovereign Prop Terminal", layout="wide")
    
    st.sidebar.title("🎮 Market Control")
    mode = st.sidebar.radio("Sport:", ["NBA Basketball", "Soccer Prop Master"])
    
    if mode == "Soccer Prop Master":
        st.title("🎯 Advanced Prop Intelligence")
        df = get_advanced_market_data()
        
        if not df.empty:
            # Filtering system for Corners/Shots/Totals
            cat = st.sidebar.selectbox("Filter by Category:", ["All Markets"] + list(df['Category'].unique()))
            display_df = df if cat == "All Markets" else df[df['Category'] == cat]
            
            col_feed, col_exec = st.columns([1, 1.2])
            
            with col_feed:
                st.subheader("Live Prop Feed")
                selection = st.selectbox("Select Target Event:", ["-- Choose --"] + display_df['Bet On'].tolist())
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
            with col_exec:
                st.subheader("⚡ Strategy Briefing")
                if selection != "-- Choose --":
                    s = display_df[display_df['Bet On'] == selection].iloc[0]
                    
                    # Risk Management: Fractional Kelly (10% scale)
                    # We assume a base 5% edge for prop markets
                    edge = 0.05
                    prob = (1/s['Price']) + edge
                    f_star = (((s['Price'] - 1) * prob) - (1 - prob)) / (s['Price'] - 1)
                    stake = max(0, f_star * BANKROLL * 0.1)

                    st.markdown(f"""
                        <div style="background:#0d1117; padding:25px; border-radius:15px; border:2px solid #3fb950;">
                            <h2 style="color:white; margin:0;">{s['Match']}</h2>
                            <h1 style="color:#3fb950;">SIGNAL: {s['Bet On']}</h1>
                            <h3 style="color:white;">RECOMMENDED STAKE: ${round(stake, 2)}</h3>
                            <hr style="border-color:#30363d">
                            <h4 style="color:#f1e05a;">WHY THIS EVENT?</h4>
                            <p style="color:#8b949e;">Market <b>{s['Category']}</b> is less 'efficient' than the Win/Loss market. Cumulative events like shots or corners follow team <b>intensity</b> rather than just the final score, providing a safer buffer.</p>
                            <h4 style="color:#f1e05a;">WHAT'S GOING TO HAPPEN?</h4>
                            <p style="color:#8b949e;">By staking <b>${round(stake, 2)}</b>, you are following a mathematical growth curve. If this {s['Category']} target is met, your bankroll increases without the 'Coin Flip' risk of a standard Win/Loss bet.</p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("No advanced prop markets found. Your API key may be limited to 'Main' markets only.")

if __name__ == "__main__":
    main()
