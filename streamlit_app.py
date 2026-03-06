import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Live Raffle Draw", layout="wide")

# -----------------------
# Custom Styling
# -----------------------
st.markdown("""
<style>
.main-title{
    text-align:center;
    font-size:60px;
    font-weight:bold;
    color:#ff4b4b;
}

.roulette{
    text-align:center;
    font-size:70px;
    font-weight:bold;
    background:#000;
    color:#00ff00;
    padding:40px;
    border-radius:20px;
}

.winner{
    text-align:center;
    font-size:80px;
    font-weight:bold;
    color:gold;
}

.info-box{
    text-align:center;
    font-size:25px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎉 LIVE RAFFLE DRAW 🎉</div>', unsafe_allow_html=True)

# -----------------------
# Session storage
# -----------------------
if "participants" not in st.session_state:
    st.session_state.participants = []

if "winners" not in st.session_state:
    st.session_state.winners = []

# -----------------------
# Upload Participants
# -----------------------
st.sidebar.header("Participants")

uploaded_file = st.sidebar.file_uploader("Upload Excel List", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    names = df.iloc[:,0].dropna().astype(str).tolist()
    st.session_state.participants = names

# -----------------------
# Event Dashboard
# -----------------------
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Participants", len(st.session_state.participants))

with col2:
    st.metric("Total Winners", len(st.session_state.winners))

# -----------------------
# Prize Settings
# -----------------------
st.sidebar.header("Prize Setup")

prize = st.sidebar.text_input("Prize Name")

num_winners = st.sidebar.number_input(
    "Number of Winners",
    min_value=1,
    value=1
)

allow_repeat = st.sidebar.checkbox("Allow repeat winners")

start_draw = st.sidebar.button("🎡 START DRAW")

roulette = st.empty()

# -----------------------
# Draw Logic
# -----------------------
if start_draw:

    available = st.session_state.participants

    if not allow_repeat:
        previous = [w["Name"] for w in st.session_state.winners]
        available = [p for p in available if p not in previous]

    if len(available) < num_winners:
        st.error("Not enough participants remaining.")
    else:

        winners = []

        for i in range(num_winners):

            # Countdown
            for i in range(3,0,-1):
                roulette.markdown(
                    f"<div class='roulette'>Drawing in {i}...</div>",
                    unsafe_allow_html=True
                )
                time.sleep(1)

            # Spin animation
            for _ in range(60):
                name = random.choice(available)

                roulette.markdown(
                    f"<div class='roulette'>{name}</div>",
                    unsafe_allow_html=True
                )

                time.sleep(0.04)

            winner = random.choice(available)

            roulette.markdown(
                f"<div class='winner'>🏆 {winner} 🏆</div>",
                unsafe_allow_html=True
            )

            st.balloons()

            winners.append(winner)
            available.remove(winner)

            time.sleep(3)

        for w in winners:
            st.session_state.winners.append({
                "Prize": prize,
                "Name": w
            })

# -----------------------
# Winner Board
# -----------------------
st.header("🏆 WINNER BOARD")

if st.session_state.winners:

    df_winners = pd.DataFrame(st.session_state.winners)

    st.dataframe(df_winners, use_container_width=True)

    csv = df_winners.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Winner Report",
        csv,
        "raffle_winners.csv",
        "text/csv"
    )

else:
    st.info("No winners yet.")
