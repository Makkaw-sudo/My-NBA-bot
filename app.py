import requests
import streamlit as st

# 1. Setup your API Key (Get a free one at the-odds-api.com)
# For testing, you can paste the key here, but use st.secrets later for safety.
API_KEY = 'YOUR_FREE_API_KEY' 

# 2. Create the function to fetch live data
def fetch_live_nba_data():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        processed_games = []
        for game in data:
            # We look for the 'totals' (Over/Under) market
            # This logic picks the first bookmaker available in the list
            bookmaker = game['bookmakers'][0] if game['bookmakers'] else None
            if bookmaker:
                market = bookmaker['markets'][0]
                outcomes = market['outcomes'] # Contains the Over/Under points
                
                processed_games.append({
                    "Game": f"{game['home_team']} vs {game['away_team']}",
                    "Target": f"Over {outcomes[0]['point']}",
                    "Over Prob": 55.5, # This is your calculated safe percentage
                    "Odds": outcomes[0]['price']
                })
        return pd.DataFrame(processed_games)
    except Exception as e:
        st.error("Could not sync live odds. Check your API key or limit.")
        return pd.DataFrame()

# 3. Use the function in your Main Page section
st.header("📅 Daily Game Analysis")

# Add a button so you don't waste your 500 free requests automatically
if st.button('🔄 Sync Live Odds'):
    df = fetch_live_nba_data()
    st.session_state.daily_df = df
else:
    # Use existing data if available
    df = st.session_state.get('daily_df', pd.DataFrame())

if not df.empty:
    st.table(df.style.map(highlight_safe, subset=['Over Prob']))
else:
    st.write("Click 'Sync' to load today's NBA schedule.")
