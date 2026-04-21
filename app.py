import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIG ---
API_KEY = '4d1e72e9dc2207f0ae744c61dfa51576' 

# --- 2. ADVANCED STYLING (The "Beauty" Layer) ---
st.set_page_config(page_title="NBA Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Fancy Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 15px;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }

    /* Card-like containers for data */
    .metric-card {
        background: #1a1f2c;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
    }
    
    /* Clean up headers */
    h1, h2, h3 {
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOGIC ---
def fetch_nba_data(market_key):
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets={market_key}&oddsFormat=decimal"
    try:
        response = requests.get(url)
        data = response.json()
        processed = []
        for game in data:
            bookie = game['bookmakers'][0] if game['bookmakers'] else None
            if bookie:
                m = bookie['markets'][0]
                processed.append({
                    "MATCHUP": f"{game['home_team']} ⚡ {game['away_team']}",
                    "TARGET LINE": f"OVER {m['outcomes'][0]['point']}",
                    "LIVE ODDS": m['outcomes'][0]['price']
                })
        return pd.DataFrame(processed)
    except:
        return pd.DataFrame()

# --- 4. APP LAYOUT ---
st.title("🏙️ NBA Terminal: Night Mode")

# Command Center
with st.container():
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        if st.button("🏟️ Game"): st.session_state.live_df = fetch_nba_data("totals")
    with c2: 
        if st.button("1️⃣ Q1"): st.session_state.live_df = fetch_nba_data("totals_q1")
    with c3: 
        if st.button("2️⃣ Q2"): st.session_state.live_df = fetch_nba_data("totals_q2")
    with c4: 
        if st.button("🔥 Live"): st.session_state.live_df = fetch_nba_data("totals_q3,totals_q4")
    st.markdown('</div>', unsafe_allow_html=True)

# Content
left, right = st.columns([2, 1], gap="large")

with left:
    st.subheader("📡 Live Market Feed")
    df = st.session_state.get('live_df', pd.DataFrame())
    if not df.empty:
        # Styled Table
        st.dataframe(df.style.set_properties(**{
            'background-color': '#161b22',
            'color': '#c9d1d9',
            'border-color': '#30363d'
        }), use_container_width=True, hide_index=True)
    else:
        st.info("Select a market above to begin analysis.")

with right:
    st.subheader("📈 Bankroll Control")
    
    if 'profit' not in st.session_state: st.session_state.profit = 0.0
    
    st.markdown(f"""
        <div style="background: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155;">
            <p style="margin:0; font-size: 0.9em; color: #94a3b8;">Session Profit</p>
            <h2 style="margin:0; color: #22c55e;">+${st.session_state.profit}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Spacer
    
    with st.expander("🧮 Smart Recovery", expanded=True):
        unit = st.number_input("Base Stake ($)", value=10.0)
        loss = st.number_input("Loss to Recover ($)", value=0.0)
        odds = st.number_input("Live Odds", value=1.91)
        
        recovery = round((loss + unit) / (odds - 1), 2)
        
        st.markdown(f"### Next Move: :green[${recovery}]")
        
        if st.button("💰 LOG WIN"):
            st.session_state.profit += unit
            st.balloons()
            st.rerun()

st.caption("v2.5 Professional Terminal | Data via The Odds API")
