import streamlit as st

st.title("💰 NBA Strategy Tracker")

# Sidebar settings
start_bet = st.sidebar.number_input("Starting Bet ($)", value=25)
line = st.sidebar.number_input("Point Line", value=51.5)

# Game Tracker
st.header("Live Game Tracking")
q = st.radio("What happened in the last quarter?", 
             ["Not Started", "Q1 Under", "Q2 Under", "Q3 Under", "✅ WIN - CHECK OUT"])

if q == "Not Started":
    st.info(f"👉 PLACE BET: ${start_bet} on Q1 Over {line}")
elif q == "Q1 Under":
    st.warning(f"👉 PLACE BET: ${start_bet * 2} on Q2 Over {line}")
elif q == "Q2 Under":
    st.warning(f"👉 PLACE BET: ${start_bet * 4} on Q3 Over {line}")
elif q == "Q3 Under":
    st.error(f"👉 FINAL BET: ${start_bet * 8} on Q4 Over {line}")
else:
    st.balloons()
    st.success(f"PROFIT: +${start_bet}! Stop betting on this game and reset.")
