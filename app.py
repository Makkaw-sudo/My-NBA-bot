import streamlit as st

# 1. Set up the page layout
st.set_page_config(page_title="Sports Betting Leads", layout="wide")

# 2. Define a function to render your HTML cards properly
def render_card(game_name, edge_val, pace_proj, live_score):
    # This is the string containing your HTML/CSS
    card_template = f"""
    <div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 20px; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="color: #8b949e; font-size: 14px; font-weight: bold; text-transform: uppercase;">
                STREAMING // {game_name}
            </div>
            <div style="background-color: rgba(63, 185, 80, 0.1); border: 1px solid #3fb950; border-radius: 12px; padding: 4px 12px; color: #3fb950; text-align: center;">
                <div style="font-size: 10px; font-weight: bold;">EDGE:</div>
                <div style="font-size: 14px; font-weight: bold;">{edge_val}%</div>
            </div>
        </div>
        
        <div style="margin-top: 15px; padding: 15px 0; border-top: 1px solid #30363d;">
            <div style="color: #3fb950; font-size: 18px; font-weight: bold; margin-bottom: 10px;">BET CHECKED</div>
            <div style="color: #f0f6fc; font-family: monospace; font-size: 14px;">
                PACE_PROJ: {pace_proj} | LIVE: {live_score}
            </div>
        </div>
    </div>
    """
    # THE FIX: This renders the string as actual HTML
    st.markdown(card_template, unsafe_allow_html=True)

# 3. Example: Displaying multiple leads
st.title("Live Betting Dashboard")

# Mock data
leads = [
    {"teams": "Boston Celtics vs Philadelphia 76ers", "edge": 2.6, "pace": 59.3, "score": "123-98"},
    {"teams": "Detroit Pistons vs Orlando Magic", "edge": 2.6, "pace": 61.2, "score": "45-52"}
]

# Loop through and display
for lead in leads:
    render_card(lead['teams'], lead['edge'], lead['pace'], lead['score'])
