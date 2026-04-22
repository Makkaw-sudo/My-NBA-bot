def get_smart_leads():
    # Ensure the market name is correct for the current API version
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=decimal"
    
    try:
        response = requests.get(url)
        data = response.json()

        # ERROR CHECK: If the API returns a dictionary with 'message', it failed
        if isinstance(data, dict) and "message" in data:
            st.error(f"API Error: {data['message']}")
            return pd.DataFrame()
        
        # ERROR CHECK: Ensure data is a list of games
        if not isinstance(data, list):
            st.error("Unexpected API Response format.")
            return pd.DataFrame()

        all_opportunities = []
        for game in data:
            home = game.get('home_team')
            away = game.get('away_team')
            
            # Matchup Stats
            h_avg = TEAM_STATS.get(home, DEFAULT_AVG)
            a_avg = TEAM_STATS.get(away, DEFAULT_AVG)
            dynamic_mean = (h_avg + a_avg) / 2 
            
            # Check if bookmakers exist
            bookmakers = game.get('bookmakers', [])
            if not bookmakers:
                continue
                
            # Loop through markets to find the 'totals'
            for market in bookmakers[0].get('markets', []):
                if market['key'] == 'totals':
                    line = market['outcomes'][0]['point']
                    
                    z_score = (line - dynamic_mean) / STD_DEV
                    prob = 0.5 * (1 + math.erf(-z_score / math.sqrt(2)))
                    
                    all_opportunities.append({
                        "Matchup": f"{home} vs {away}",
                        "Line": line,
                        "Exp Score": round(dynamic_mean, 1),
                        "Prob": round(prob * 100, 1),
                        "Edge": round(dynamic_mean - line, 2)
                    })
        
        return pd.DataFrame(all_opportunities).sort_values(by="Prob", ascending=False)

    except Exception as e:
        st.error(f"System Error: {str(e)}")
        return pd.DataFrame()
