def calculate_quant_logic(h_team, a_team, live_line, time_left, current_score, step, base_unit):
    # 1. FIX: Quarter-Specific PPM (Points Per Minute)
    # Total game PPM is ~4.9. We ensure we only calculate for the REMAINING minutes.
    h_ppm = TEAM_METRICS.get(h_team, 2.45) # Average individual team PPM is ~2.45
    a_ppm = TEAM_METRICS.get(a_team, 2.45)
    combined_ppm = h_ppm + a_ppm
    
    # Projection = Current Score + (Pace * Remaining Time)
    projected_remaining = combined_ppm * time_left
    final_projection = current_score + projected_remaining
    
    # 2. Martingale Math (Recovery Formula)
    odds = 1.91 
    total_lost = sum([base_unit * (2**i) for i in range(step - 1)])
    stake = round((total_lost + base_unit) / (odds - 1), 2)
    
    # 3. FIX: Realistic Poisson Probability
    # Use the 'final_projection' as the mean (mu) for the Poisson distribution
    prob_over = (1 - poisson.cdf(live_line, final_projection)) * 100
    
    # 4. SAFETY: Table Limit Check
    # Most bookmakers limit quarter bets. Let's set a logical alert.
    TABLE_LIMIT = 500.0  # Adjust this to your bookie's limit
    limit_alert = True if stake > TABLE_LIMIT else False
    
    # Direction & Confidence
    edge = final_projection - live_line
    direction = "OVER" if edge > 0 else "UNDER"
    
    # Confidence is now based on realistic margins (2-4 points is a strong edge)
    if abs(edge) > 3.0:
        confidence = "HIGH"
    elif abs(edge) > 1.5:
        confidence = "MODERATE"
    else:
        confidence = "LOW"
    
    return stake, direction, round(prob_over, 1), confidence, round(final_projection, 1), limit_alert
