def calculate_bet(stake, odds, odds_type='decimal'):
    """
    Calculates the potential win and net profit.
    :param stake: The amount of money wagered.
    :param odds: The odds offered (Decimal or American).
    :param odds_type: 'decimal' or 'american'.
    """
    if odds_type == 'decimal':
        # Potential Win = Stake * Decimal Odds
        potential_win = stake * odds
    
    elif odds_type == 'american':
        if odds > 0:
            # Positive American odds (e.g., +150)
            potential_win = stake * (1 + (odds / 100))
        else:
            # Negative American odds (e.g., -110)
            potential_win = stake * (1 + (100 / abs(odds)))
    
    else:
        return "Unsupported odds type."

    net_profit = potential_win - stake
    
    return {
        "Stake": f"${stake:.2f}",
        "Potential Win (Total Payout)": f"${potential_win:.2f}",
        "Net Profit": f"${net_profit:.2f}"
    }

# Example usage:
# A $100 bet on odds of 2.50
result = calculate_bet(100, 2.50)
print(result)
