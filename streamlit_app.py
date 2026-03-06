import streamlit as st
import pandas as pd
import random
import time
from PIL import Image

st.set_page_config(page_title="LMPC Raffle Draw", layout="wide")

# ----------------------------
# Load Logo
# ----------------------------
logo = Image.open("logo.jpg.jpg")

# ----------------------------
# Custom Theme (Based on Logo)
# ----------------------------
st.markdown("""
<style>

.stApp{
background: linear-gradient(to bottom,#e6f4ff,#ffffff);
}

.title{
text-align:center;
font-size:55px;
font-weight:bold;
color:#d60000;
}

.subtitle{
text-align:center;
font-size:28px;
color:#ff7a00;
}

.roulette{
text-align:center;
font-size:65px;
font-weight:bold;
background:#0f4c81;
color:white;
padding:40px;
border-radius:20px;
margin-top:20px;
}

.winner{
text-align:center;
font-size:75px;
font-weight:bold;
color:#ff7a00;
padding:30px;
}

.name-list{
height:400px;
overflow-y:scroll;
background:white;
padding:15px;
border-radius:10px;
border:2px solid #0f4c81;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header Section
# ----------------------------
col1,col2,col3 = st.columns([1,2,1])

with col2:
    st.image(logo,width=300)

st.markdown('<div class="title">LODLOD MULTI-PURPOSE COOPERATIVE</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🎉 RAFFLE DRAW SYSTEM 🎉</div>', unsafe_allow_html=True)

st.divider()

# ----------------------------
# Upload Excel
# ----------------------------
st.sidebar.header("Upload Participants")

uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

if "participants" not in st.session_state:
    st.session_state.participants = []

if "winners" not in st.session_state:
    st.session_state.winners = []

if uploaded_file:

    df = pd.read_excel(uploaded_file, engine="openpyxl")

    names = df.iloc[:,0].dropna().astype(str).tolist()

    st.session_state.participants = names

# ----------------------------
# Dashboard
# ----------------------------
col1,col2 = st.columns(2)

with col1:
    st.metric("Total Participants", len(st.session_state.participants))

with col2:
    st.metric("Total Winners", len(st.session_state.winners))

# ----------------------------
# Display Participant List
# ----------------------------
st.subheader("Participant List")

if st.session_state.participants:

    name_df = pd.DataFrame(st.session_state.participants, columns=["Name"])

    st.dataframe(name_df, height=400)

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

draw_button = st.sidebar.button("🎡 START DRAW")

roulette = st.empty()

# ----------------------------
# Draw Logic
# ----------------------------
if draw_button:

    available = st.session_state.participants.copy()

    previous = [w["Name"] for w in st.session_state.winners]

    available = [p for p in available if p not in previous]

    if len(available) < winner_count:
        st.error("Not enough participants remaining.")
    else:

        winners = []

        for i in range(winner_count):

            for i in range(3,0,-1):

                roulette.markdown(
                f"<div class='roulette'>Drawing in {i}...</div>",
                unsafe_allow_html=True
                )

                time.sleep(1)

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
                "Prize":prize,
                "Name":w
            })

# ----------------------------
# Winner Board
# ----------------------------
st.header("🏆 Winner Board")

if st.session_state.winners:

    df_winners = pd.DataFrame(st.session_state.winners)

    st.dataframe(df_winners,use_container_width=True)

    csv = df_winners.to_csv(index=False).encode("utf-8")

    st.download_button(
    "Download Winner Report",
    csv,
    "raffle_winners.csv",
    "text/csv"
    )
