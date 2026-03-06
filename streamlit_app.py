import streamlit as st
import pandas as pd
import random
import time
import os
import base64

st.set_page_config(page_title="LMPC Raffle", layout="wide")

# -------------------------
# Helpers
# -------------------------
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def play_spin_sound(file_path):

    if os.path.exists(file_path):

        with open(file_path, "rb") as f:
            data = f.read()

        b64 = base64.b64encode(data).decode()

        audio_html = f"""
        <audio autoplay loop>
            <source src="data:audio/mp4;base64,{b64}" type="audio/mp4">
        </audio>
        """

        st.markdown(audio_html, unsafe_allow_html=True)


def play_winner_sound(file_path):

    if os.path.exists(file_path):

        with open(file_path, "rb") as f:
            data = f.read()

        b64 = base64.b64encode(data).decode()

        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp4;base64,{b64}" type="audio/mp4">
        </audio>
        """

        st.markdown(audio_html, unsafe_allow_html=True)


def load_names_from_excel(uploaded_file):

    df = pd.read_excel(uploaded_file, engine="openpyxl")

    names = (
        df.iloc[:,0]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )

    return names


# -------------------------
# Session State
# -------------------------
if "participants" not in st.session_state:
    st.session_state.participants = []

if "winners" not in st.session_state:
    st.session_state.winners = []


# -------------------------
# Styling
# -------------------------
st.markdown("""
<style>

.block-container{
padding-top:1rem;
}

.main-title{
text-align:center;
font-size:42px;
font-weight:800;
color:#2c3e50;
}

.sub-title{
text-align:center;
font-size:22px;
color:#6c757d;
margin-bottom:10px;
}

.draw-title{
text-align:center;
font-size:30px;
font-weight:800;
color:#ff4b4b;
margin-top:10px;
}

.draw-box{
background:#111;
padding:70px;
border-radius:20px;
text-align:center;
font-size:60px;
color:#00ff88;
}

.winner-box{
background:#111;
padding:80px;
border-radius:20px;
text-align:center;
font-size:90px;
font-weight:bold;
color:gold;
}

.small-note{
text-align:center;
color:#6c757d;
font-size:14px;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# Logo
# -------------------------
logo_b64 = get_base64_image("logo.png")

if logo_b64:
    st.markdown(
    f"""
    <div style="text-align:center">
    <img src="data:image/png;base64,{logo_b64}" width="150">
    </div>
    """,
    unsafe_allow_html=True
    )


# -------------------------
# Header
# -------------------------
st.markdown('<div class="main-title">LODLOD MULTI-PURPOSE COOPERATIVE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🎉 LIVE RAFFLE DRAW SYSTEM 🎉</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Transparent live raffle draw</div>', unsafe_allow_html=True)

st.divider()


# -------------------------
# Sidebar
# -------------------------
st.sidebar.header("Upload Participants")

uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:

    try:

        st.session_state.participants = load_names_from_excel(uploaded_file)

        st.sidebar.success(f"{len(st.session_state.participants)} participants loaded")

    except Exception as e:

        st.sidebar.error(str(e))


st.sidebar.header("Prize Setup")

prize = st.sidebar.text_input("Prize Name", value="Special Prize")

winner_count = st.sidebar.number_input(
"Number of Winners",
min_value=1,
value=1
)

start_draw = st.sidebar.button("🎡 START RAFFLE DRAW", use_container_width=True)


# -------------------------
# Metrics
# -------------------------
col1,col2,col3 = st.columns(3)

with col1:
    st.metric("Participants", len(st.session_state.participants))

with col2:
    st.metric("Winners", len(st.session_state.winners))

with col3:
    previous = [w["Name"] for w in st.session_state.winners]

    remaining = len([p for p in st.session_state.participants if p not in previous])

    st.metric("Remaining Eligible", remaining)


# -------------------------
# Participant List
# -------------------------
show_list = st.toggle("Show Participant List", value=True)

if show_list:

    st.subheader("Participant List")

    if st.session_state.participants:

        df_names = pd.DataFrame(
        st.session_state.participants,
        columns=["Name"]
        )

        df_names.index = df_names.index + 1
        df_names.index.name = "No."

        st.dataframe(df_names, height=300, use_container_width=True)

    else:
        st.info("Upload an Excel file to display participants")


# -------------------------
# Draw Area
# -------------------------
st.markdown('<div class="draw-title">🎯 DRAW AREA</div>', unsafe_allow_html=True)

draw_placeholder = st.empty()


# -------------------------
# Draw Logic
# -------------------------
if start_draw:

    available = st.session_state.participants.copy()

    previous = [w["Name"] for w in st.session_state.winners]

    available = [p for p in available if p not in previous]

    if len(available) < winner_count:

        st.error("Not enough participants remaining.")

    else:

        winners = []

        for i in range(winner_count):

            # start spin sound
            play_spin_sound("spin.m4a")

            delay = 0.015

            for _ in range(70):

                name = random.choice(available)

                draw_placeholder.markdown(
                f'<div class="draw-box">{name}</div>',
                unsafe_allow_html=True
                )

                time.sleep(delay)

                delay += 0.0015


            winner = random.choice(available)

            draw_placeholder.markdown(
            f'<div class="winner-box">🏆 {winner} 🏆</div>',
            unsafe_allow_html=True
            )

            # play winner sound
            play_winner_sound("winner.m4a")

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
st.header("🏆 Winner Board")

if st.session_state.winners:

    df_winners = pd.DataFrame(st.session_state.winners)

    df_winners.index = df_winners.index + 1
    df_winners.index.name = "No."

    st.dataframe(df_winners, use_container_width=True)

    csv = df_winners.to_csv(index=False).encode("utf-8")

    st.download_button(
    "Download Winner Report",
    csv,
    "raffle_winners.csv",
    "text/csv",
    use_container_width=True
    )

else:

    st.info("No winners yet.")
