import requests
import math

class QuantumTitanAI:
    def __init__(self, base_stake, bankroll):
        self.base_stake = base_stake
        self.bankroll = bankroll
        self.current_step = 0  # Martingale level (0, 1, 2, 3...)
        self.total_loss = 0

    def calculate_ev(self, prob, odds):
        """ Calculates Expected Value. Only +EV bets are considered. """
        return (prob * odds) - 1

    def martingale_manager(self, odds):
        """ 
        Calculates the stake needed to recover all losses + target profit.
        Formula: (Total Loss + Base Stake) / (Odds - 1)
        """
        if self.current_step >= 4: # SAFETY CAP: Reset after 4 losses
            self.reset_progression()
            return self.base_stake, "⚠️ RESET: Max levels reached. Starting over."
        
        # Dynamic recovery multiplier (safely handles 1.6+ odds)
        stake = (self.total_loss + self.base_stake) / (odds - 1)
        return round(stake, 2), f"Step {self.current_step + 1}"

    def select_perfect_odd(self, market_options):
        """
        Market Competition: Scans different markets and picks the 'Perfect' one.
        Expects a list of dicts: [{'market': 'NBA Over', 'prob': 0.72, 'odds': 1.65}, ...]
        """
        best_market = None
        highest_edge = 0

        for option in market_options:
            edge = self.calculate_ev(option['prob'], option['odds'])
            
            # The Selection Filter: Needs >65% prob and +EV edge
            if option['prob'] >= 0.65 and edge > highest_edge:
                highest_edge = edge
                best_market = option

        return best_market

    def execute_signal(self, market_options):
        selection = self.select_perfect_odd(market_options)
        
        if selection:
            stake, level = self.martingale_manager(selection['odds'])
            message = (
                f"🎯 **SMART SIGNAL DETECTED**\n"
                f"Market: {selection['market']}\n"
                f"Odds: {selection['odds']} | Prob: {selection['prob']:.1%}\n"
                f"Instruction: {level}\n"
                f"Required Stake: ${stake}"
            )
            return message
        return "⏳ Scanning... No 'Perfect' odds found currently."

    def reset_progression(self):
        self.current_step = 0
        self.total_loss = 0

# --- INITIALIZATION ---
# Starting with a $10 base stake
bot = QuantumTitanAI(base_stake=10, bankroll=1000)

# --- EXAMPLE LIVE SCAN ---
live_opportunities = [
    {'market': 'NBA Live Quarter (Pace Logic)', 'prob': 0.74, 'odds': 1.62},
    {'market': 'Football Corners (Wing Play)', 'prob': 0.68, 'odds': 1.75},
    {'market': 'Yellow Cards (Referee Strict)', 'prob': 0.55, 'odds': 2.10}
]

print(bot.execute_signal(live_opportunities))
