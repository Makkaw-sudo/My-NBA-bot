class MartingaleManager:
    def __init__(self, base_stake=100, max_quarters=4):
        self.base_stake = base_stake
        self.max_quarters = max_quarters
        # We use a dictionary to track multiple games at once
        self.game_states = {} 

    def get_current_bet(self, game_id):
        """Calculates what the stake should be for the current quarter."""
        if game_id not in self.game_states:
            self.game_states[game_id] = {"quarter": 1, "losses": 0}
            
        current_loss_count = self.game_states[game_id]["losses"]
        # Formula: Base Stake * (2 ^ number of consecutive losses)
        return self.base_stake * (2 ** current_loss_count)

    def record_result(self, game_id, won):
        """Updates the state based on whether the last quarter was a win or loss."""
        if game_id not in self.game_states:
            return

        if won:
            # WIN: Strategy successful, reset this game
            self.game_states[game_id] = {"quarter": 1, "losses": 0, "status": "COMPLETED"}
        else:
            # LOSS: Move to next quarter and increase loss count
            self.game_states[game_id]["quarter"] += 1
            self.game_states[game_id]["losses"] += 1
            
            # Check if we hit the 4th quarter limit
            if self.game_states[game_id]["quarter"] > self.max_quarters:
                self.game_states[game_id]["status"] = "BUST"

# --- EXAMPLE USAGE ---
manager = MartingaleManager(base_stake=50) # Start with $50

# Game 1: First Quarter
bet_q1 = manager.get_current_bet("Lakers_Game") 
print(f"Q1 Bet: ${bet_q1}") # Output: $50

# Logic: We lost Q1
manager.record_result("Lakers_Game", won=False)

# Game 1: Second Quarter
bet_q2 = manager.get_current_bet("Lakers_Game")
print(f"Q2 Bet: ${bet_q2}") # Output: $100
