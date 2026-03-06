import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(
    page_title="LMPC Raffle Draw",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Styling
# ----------------------------
st.markdown("""
<style>

.stApp{
background-color:#f5f7fb;
color:#000000;
}

/* Main titles */
.title{
text-align:center;
font-size:55px;
font-weight:bold;
color:#2c3e50;
}

.subtitle{
text-align:center;
font-size:28px;
color:#6c757d;
}

/* Roulette display */
.roulette{
text-align:center;
font-size:70px;
font-weight:bold;
background:#111;
color:#00ff88;
padding:40px;
border-radius:20px;
margin-top:20px;
}

/* Winner display */
.winner{
text-align:center;
font-size:80px;
font-weight:bold;
color:#ff4b4b;
padding:30px;
}

/* Fix text visibility in dark mode */
[data-testid="stAppViewContainer"]{
color:white;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header
# ----------------------------
st.markdown('<div class="title">LODLOD MULTI-PURPOSE COOPERATIVE</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🎉 LIVE RAFFLE DRAW SYSTEM 🎉</div>', unsafe_allow_html=True)

st.divider()

# ----------------------------
# Session State
# ----------------------------
if "participants" not in st.session_state:
    st.session_state.participants = []

if "winners" not in st.session_state:
    st.session_state.winners = []

# ----------------------------
# Upload Excel
# ----------------------------
st.sidebar.header("Upload Participants")

uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    names = df.iloc[:,0].dropna().astype(str).tolist()
    st.session_state.participants = names

# ----------------------------
# Dashboard
# ----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Participants", len(st.session_state.participants))

with col2:
    st.metric("Total Winners", len(st.session_state.winners))

with col3:
    remaining = len(st.session_state.participants) - len(st.session_state.winners)
    st.metric("Remaining Eligible", remaining)

# ----------------------------
# Participant List
# ----------------------------
st.subheader("Participant List")

if st.session_state.participants:
    df_names = pd.DataFrame(st.session_state.participants, columns=["Name"])
    st.dataframe(df_names, height=400)

# ----------------------------
# Prize Settings
# ----------------------------
st.sidebar.header("Prize Setup")

prize = st.sidebar.text_input("Prize Name")

winner_count = st.sidebar.number_input(
    "Number of Winners",
    min_value=1,
    value=1
)

start_draw = st.sidebar.button("🎡 START DRAW")

roulette = st.empty()

# ----------------------------
# Draw Logic
# ----------------------------
if start_draw:

    available = st.session_state.participants.copy()

    previous = [w["Name"] for w in st.session_state.winners]

    available = [p for p in available if p not in previous]

    if len(available) < winner_count:
        st.error("Not enough participants remaining.")
    else:

        winners = []

        for i in range(winner_count):

            # countdown
            for i in range(3,0,-1):
                roulette.markdown(
                    f"<div class='roulette'>Drawing in {i}...</div>",
                    unsafe_allow_html=True
                )
                time.sleep(1)

            # roulette spin
            for _ in range(60):

                name = random.choice(available)

                roulette.markdown(
                    f"<div class='roulette'>{name}</div>",
                    unsafe_allow_html=True
                )

                time.sleep(0.05)

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

# ----------------------------
# Winner Board
# ----------------------------
st.header("🏆 Winner Board")

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
