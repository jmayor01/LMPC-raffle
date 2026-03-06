import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="LMPC Raffle", layout="wide")

# -------------------------
# Custom Styling
# -------------------------
st.markdown("""
<style>

.stApp{
background-color: var(--background-color);
}

/* Header */
.title{
text-align:center;
font-size:50px;
font-weight:bold;
color:#ff4b4b;
}

.subtitle{
text-align:center;
font-size:24px;
font-weight:500;
color:#2c3e50;
}

/* Draw container */
.draw-box{
background:#111;
border-radius:20px;
padding:50px;
margin-top:20px;
text-align:center;
box-shadow:0px 8px 25px rgba(0,0,0,0.3);
}

/* Roulette names */
.roulette{
font-size:60px;
font-weight:bold;
color:#00ff88;
}

/* Winner highlight */
.winner{
font-size:80px;
font-weight:bold;
color:#ffd700;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# Header with Logo
# -------------------------
col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.image("logo.png", width=180)

st.markdown('<div class="title">LODLOD MULTI-PURPOSE COOPERATIVE</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🎉 LIVE RAFFLE DRAW 🎉</div>', unsafe_allow_html=True)

st.divider()

# -------------------------
# Session State
# -------------------------
if "participants" not in st.session_state:
    st.session_state.participants = []

if "winners" not in st.session_state:
    st.session_state.winners = []

# -------------------------
# Upload Participants
# -------------------------
st.sidebar.header("Upload Participants")

uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    names = df.iloc[:,0].dropna().astype(str).tolist()
    st.session_state.participants = names

# -------------------------
# Stats Dashboard
# -------------------------
col1,col2,col3 = st.columns(3)

with col1:
    st.metric("Participants", len(st.session_state.participants))

with col2:
    st.metric("Winners", len(st.session_state.winners))

with col3:
    remaining = len(st.session_state.participants) - len(st.session_state.winners)
    st.metric("Remaining", remaining)

# -------------------------
# Participant List
# -------------------------
st.subheader("Participant List")

if st.session_state.participants:

    df_names = pd.DataFrame(
        st.session_state.participants,
        columns=["Name"]
    )

    st.dataframe(df_names, height=300)

# -------------------------
# Prize Settings
# -------------------------
st.sidebar.header("Prize Setup")

prize = st.sidebar.text_input("Prize Name")

winner_count = st.sidebar.number_input(
    "Number of Winners",
    min_value=1,
    value=1
)

draw_button = st.sidebar.button("🎡 START DRAW")

# -------------------------
# Draw Section (Highlighted)
# -------------------------
st.markdown("## 🎯 DRAW AREA")

draw_placeholder = st.empty()

# -------------------------
# Draw Logic
# -------------------------
if draw_button:

    available = st.session_state.participants.copy()

    previous = [w["Name"] for w in st.session_state.winners]

    available = [p for p in available if p not in previous]

    if len(available) < winner_count:
        st.error("Not enough participants remaining.")
    else:

        winners = []

        for i in range(winner_count):

            # Countdown
            for x in range(3,0,-1):

                draw_placeholder.markdown(
                f"""
                <div class="draw-box">
                <div class="roulette">Drawing in {x}...</div>
                </div>
                """,
                unsafe_allow_html=True
                )

                time.sleep(1)

            # Roulette animation
            for _ in range(60):

                name = random.choice(available)

                draw_placeholder.markdown(
                f"""
                <div class="draw-box">
                <div class="roulette">{name}</div>
                </div>
                """,
                unsafe_allow_html=True
                )

                time.sleep(0.05)

            winner = random.choice(available)

            draw_placeholder.markdown(
            f"""
            <div class="draw-box">
            <div class="winner">🏆 {winner} 🏆</div>
            </div>
            """,
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

# -------------------------
# Winner Board
# -------------------------
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
