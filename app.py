def calculate_advanced_move(step, current_odds, team_volatility):
    # If the team is 'High Volatility' (unpredictable), 
    # we increase the safety margin for our Martingale.
    safety_buffer = 1.10 if team_volatility == "High" else 1.0
    
    # Advanced Stake Calculation including 'Leakage' (fees/conversion)
    target_profit = 20.0
    previous_losses = 45.0 # Example
    
    stake = (previous_losses + target_profit) / (current_odds - 1)
    adjusted_stake = round(stake * safety_buffer, 2)
    
    return f"🚨 HIGH VOLATILITY DETECTED: Bet ${adjusted_stake} for safety."
