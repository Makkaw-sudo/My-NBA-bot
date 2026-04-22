import streamlit as st

# --- 1. CORE ENGINE ---
class QuantumTitanEngine:
    def __init__(self, base_stake, stop_loss, max_stake):
        self.base_stake = base_stake
        self.stop_loss = stop_loss
        self.max_stake = max_stake

    def get_bet_logic(self, current_loss, odds):
        """Calculates stake and potential payout."""
        if current_loss >= self.stop_loss:
            return None, "STOP-LOSS HIT"
        if odds <= 1.0: return 0.0, 0.0
        
        stake = (current_loss + self.base_stake) / (odds - 1)
        if stake > self.max_stake:
            return None, "LIMIT EXCEEDED"
            
        return round(float(stake), 2), round(float(stake * odds), 2)

# --- 2. SESSION STATE (The Brain of the App) ---
if 'cycle_loss' not in st.session_state: st.session_state.cycle_loss = 0.0
if 'active_bet' not in st.session_state: st.session_state.active_bet = None

# --- 3. UI SETUP ---
st.set_page_config(page_title="QUANTUM TITAN V11", layout="wide")
st.title("🚀 QUANTUM TITAN V11: Live Execution Mode")

# SIDEBAR: Risk Management
st.sidebar.header("🛡️ Risk & Recovery")
base_amt = st.sidebar.number_input("Base Stake ($)", value=10.0)
max_l = st.sidebar.number_input("Stop-Loss ($)", value=200.0)
cap_s = st.sidebar.number_input("Max Bet ($)", value=150.0)

# Current Bankroll Status
st.sidebar.markdown("---")
st.sidebar.metric("Current Cycle Loss", f"${st.session_state.cycle_loss}")
if st.sidebar.button("🔄 Reset Cycle Manually"):
    st.session_state.cycle_loss = 0.0
    st.session_state.active_bet = None
    st.rerun()

engine = QuantumTitanEngine(base_amt, max_l, cap_s)

# --- 4. GAME DATA (OVERS ONLY) ---
nba_feed = [
    {'id': 'nba1', 'match': 'Orlando @ Detroit', 'market': 'Q1 Over 51.5', 'odds': 1.72},
    {'id': 'nba2', 'match': 'Phoenix @ OKC', 'market': 'Q1 Over 53.5', 'odds': 1.68}
]
foot_feed = [
    {'id': 'foot1', 'match': 'AS FAR vs RS Berkane', 'market': 'Over 1.5 Goals', 'odds': 1.58},
    {'id': 'foot2', 'match': 'Man City @ Burnley', 'market': 'Over 2.5 Goals', 'odds': 1.65}
]

# --- 5. BETTING BAR FUNCTION ---
def render_betting_bar(game):
    stake, payout = engine.get_bet_logic(st.session_state.cycle_loss, game['odds'])
    
    with st.container():
        c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
        c1.markdown(f"**{game['match']}**\n\n<span style='color:green;'>📈 {game['market']}</span>", unsafe_allow_html=True)
        c2.metric("Odds", f"{game['odds']}")
        
        if isinstance(stake, float):
            c3.metric("Stake", f"${stake}")
            # The "I BET ON IT" Button
            if st.session_state.active_bet == game['id']:
                c4.warning("🎯 BET ACTIVE")
                res_col1, res_col2 = c4.columns(2)
                if res_col1.button("✅ WIN", key=f"w_{game['id']}"):
                    st.session_state.cycle_loss = 0.0
                    st.session_state.active_bet = None
                    st.balloons()
                    st.rerun()
                if res_col2.button("❌ LOSS", key=f"l_{game['id']}"):
                    st.session_state.cycle_loss += stake
                    st.session_state.active_bet = None
                    st.rerun()
            elif st.session_state.active_bet is None:
                if c4.button("🚀 I BET ON IT", key=f"btn_{game['id']}"):
                    st.session_state.active_bet = game['id']
                    st.rerun()
            else:
                c4.info("Finish active bet first")
        else:
            c3.error(stake)
        st.markdown("---")

# --- 6. DASHBOARD TABS ---
tab1, tab2 = st.tabs(["🏀 NBA Quarters", "⚽ Elite Football"])

with tab1:
    for g in nba_feed: render_betting_bar(g)
with tab2:
    for g in foot_feed: render_betting_bar(g)
