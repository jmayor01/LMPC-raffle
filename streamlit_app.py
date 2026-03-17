import streamlit as st
import pandas as pd
import random
import time
import os
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="LMPC Raffle", layout="wide")

# -------------------------
# Helpers
# -------------------------
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def play_winner_sound(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()

        b64 = base64.b64encode(data).decode()
        audio_id = str(time.time()).replace(".", "")

        components.html(
            f"""
            <audio id="winner_{audio_id}">
                <source src="data:audio/mp4;base64,{b64}" type="audio/mp4">
            </audio>
            <script>
                const audio = document.getElementById("winner_{audio_id}");
                audio.currentTime = 0;
                audio.play().catch(() => {});
            </script>
            """,
            height=0
        )


def load_names_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    names = (
        df.iloc[:, 0]
        .dropna()
        .astype(str)
        .str.strip()
    )

    return names[names != ""].drop_duplicates().tolist()


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
}

.multi-winner-box{
background:#111;
padding:40px;
border-radius:20px;
color:white;
}

.multi-winner-title{
text-align:center;
font-size:28px;
font-weight:800;
color:gold;
margin-bottom:20px;
}

.multi-winner-grid{
display:grid;
gap:16px;
}

.cols-2{ grid-template-columns: repeat(2, 1fr); }
.cols-3{ grid-template-columns: repeat(3, 1fr); }
.cols-4{ grid-template-columns: repeat(4, 1fr); }

.multi-winner-item{
background:#1c1c1c;
border:2px solid gold;
border-radius:14px;
padding:16px;
text-align:center;
font-size:28px;
font-weight:bold;
color:gold;
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
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    st.session_state.participants = load_names_from_excel(uploaded_file)

prize = st.sidebar.text_input("Prize Name", value="Special Prize")
winner_count = st.sidebar.number_input("Number of Winners", min_value=1, value=1)
start_draw = st.sidebar.button("🎡 START DRAW")


# -------------------------
# Metrics
# -------------------------
col1, col2, col3 = st.columns(3)

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
if st.toggle("Show Participant List", True):
    df = pd.DataFrame(st.session_state.participants, columns=["Name"])
    df.index += 1
    df.index.name = "No."
    st.dataframe(df, use_container_width=True)


# -------------------------
# Remaining Eligible List
# -------------------------
st.subheader("Remaining Eligible Participants")

previous = [w["Name"] for w in st.session_state.winners]
remaining_list = [p for p in st.session_state.participants if p not in previous]

if remaining_list:
    df_rem = pd.DataFrame(remaining_list, columns=["Name"])
    df_rem.index += 1
    df_rem.index.name = "No."
    st.dataframe(df_rem, use_container_width=True)
else:
    st.success("All participants have already won.")


# -------------------------
# Draw Area
# -------------------------
st.markdown('<div class="draw-title">🎯 DRAW AREA</div>', unsafe_allow_html=True)
draw_placeholder = st.empty()


# -------------------------
# Draw Logic
# -------------------------
if start_draw:

    available = [p for p in st.session_state.participants if p not in previous]

    if len(available) < winner_count:
        st.error("Not enough participants.")
    else:

        selected_winners = random.sample(available, winner_count)

        # determine columns
        if winner_count <= 6:
            grid_class = "cols-2"
        elif winner_count <= 12:
            grid_class = "cols-3"
        else:
            grid_class = "cols-4"

        # animation
        for _ in range(60):

            preview = random.sample(available, min(winner_count, len(available)))

            html = "".join(
                [f'<div class="multi-winner-item">{n}</div>' for n in preview]
            )

            draw_placeholder.markdown(
                f"""
                <div class="multi-winner-box">
                    <div class="multi-winner-title">Drawing...</div>
                    <div class="multi-winner-grid {grid_class}">
                    {html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            time.sleep(0.03)

        # final display
        if winner_count == 1:
            draw_placeholder.markdown(
                f'<div class="winner-box">🏆 {selected_winners[0]} 🏆</div>',
                unsafe_allow_html=True
            )
        else:
            final_html = "".join(
                [f'<div class="multi-winner-item">🏆 {n}</div>' for n in selected_winners]
            )

            draw_placeholder.markdown(
                f"""
                <div class="multi-winner-box">
                    <div class="multi-winner-title">WINNERS</div>
                    <div class="multi-winner-grid {grid_class}">
                    {final_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        play_winner_sound("winner.m4a")
        st.balloons()

        for w in selected_winners:
            st.session_state.winners.append({"Prize": prize, "Name": w})


# -------------------------
# Winner Board
# -------------------------
st.header("🏆 Winner Board")

if st.session_state.winners:
    df = pd.DataFrame(st.session_state.winners)
    df.index += 1
    df.index.name = "No."
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "winners.csv"
    )
else:
    st.info("No winners yet.")
