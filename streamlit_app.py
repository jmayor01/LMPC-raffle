import streamlit as st
import pandas as pd
import random
import time
import os
import base64
import streamlit.components.v1 as components

st.set_page_config(
    page_title="LMPC Raffle",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Helpers
# -------------------------
def get_base64_image(image_path: str) -> str:
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def play_winner_sound(file_path: str) -> None:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()

        b64 = base64.b64encode(data).decode()
        audio_id = str(time.time()).replace(".", "")

        components.html(
            f"""
            <html>
              <body style="margin:0;padding:0;">
                <audio id="winner_{audio_id}">
                  <source src="data:audio/mp4;base64,{b64}" type="audio/mp4">
                </audio>
                <script>
                  const audio = document.getElementById("winner_{audio_id}");
                  audio.currentTime = 0;
                  audio.play().catch(() => null);
                </script>
              </body>
            </html>
            """,
            height=0,
        )


def load_names_from_excel(uploaded_file) -> list[str]:
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    names = (
        df.iloc[:, 0]
        .dropna()
        .astype(str)
        .str.strip()
    )

    names = names[names != ""].drop_duplicates().tolist()
    return names


def get_remaining_participants() -> list[str]:
    previous_winners = [w["Name"] for w in st.session_state.winners]
    return [p for p in st.session_state.participants if p not in previous_winners]


def get_grid_class(winner_count: int) -> str:
    if winner_count <= 6:
        return "cols-2"
    if winner_count <= 12:
        return "cols-3"
    return "cols-4"


# -------------------------
# Session State
# -------------------------
if "participants" not in st.session_state:
    st.session_state.participants = []

if "winners" not in st.session_state:
    st.session_state.winners = []


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
winner_count = st.sidebar.number_input("Number of Winners", min_value=1, value=1, step=1)
event_mode = st.sidebar.toggle("🎬 Fullscreen Event Mode", value=False)

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
    margin-bottom:0.2rem;
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
    margin-bottom:16px;
}

.logo-wrap{
    text-align:center;
    margin-bottom:6px;
}

.multi-winner-box{
    background:#111;
    padding:40px;
    border-radius:20px;
    color:white;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
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

.cols-2{
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.cols-3{
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.cols-4{
    grid-template-columns: repeat(4, minmax(0, 1fr));
}

.multi-winner-item{
    background:#1c1c1c;
    border:2px solid gold;
    border-radius:14px;
    padding:16px;
    text-align:center;
    font-size:28px;
    font-weight:bold;
    color:gold;
    word-wrap:break-word;
}

.winner-box{
    background:#111;
    padding:80px;
    border-radius:20px;
    text-align:center;
    font-size:90px;
    font-weight:bold;
    color:gold;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    word-wrap:break-word;
}

.small-note{
    text-align:center;
    color:#6c757d;
    font-size:14px;
}

.floating-draw-wrap{
    margin-top: 0.75rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

if event_mode:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    .main .block-container {
        padding-top: 0.75rem !important;
        padding-bottom: 0.75rem !important;
        max-width: 100% !important;
    }

    .main-title{
        font-size:56px !important;
    }

    .sub-title{
        font-size:28px !important;
    }

    .draw-title{
        font-size:40px !important;
        margin-top:0.5rem !important;
        margin-bottom:1rem !important;
    }

    .winner-box{
        font-size:130px !important;
        padding:120px 60px !important;
    }

    .multi-winner-title{
        font-size:42px !important;
    }

    .multi-winner-item{
        font-size:42px !important;
        padding:24px !important;
    }

    .multi-winner-box{
        padding:48px !important;
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
        <div class="logo-wrap">
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
# Metrics
# -------------------------
remaining_list = get_remaining_participants()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Participants", len(st.session_state.participants))
with col2:
    st.metric("Winners", len(st.session_state.winners))
with col3:
    st.metric("Remaining Eligible", len(remaining_list))

# -------------------------
# Non-event mode tables
# -------------------------
participant_placeholder = None
remaining_placeholder = None
winner_board_placeholder = None

def render_participant_list() -> None:
    if participant_placeholder is None:
        return

    with participant_placeholder.container():
        st.subheader("Participant List")

        if st.session_state.participants:
            df_names = pd.DataFrame(st.session_state.participants, columns=["Name"])
            df_names.index = df_names.index + 1
            df_names.index.name = "No."
            st.dataframe(df_names, height=300, use_container_width=True)
        else:
            st.info("Upload an Excel file to display participants")


def render_remaining_list() -> None:
    if remaining_placeholder is None:
        return

    with remaining_placeholder.container():
        st.subheader("Remaining Eligible Participants")

        if st.session_state.participants:
            current_remaining = get_remaining_participants()

            if current_remaining:
                df_remaining = pd.DataFrame(current_remaining, columns=["Name"])
                df_remaining.index = df_remaining.index + 1
                df_remaining.index.name = "No."
                st.dataframe(df_remaining, height=300, use_container_width=True)
            else:
                st.success("All participants have already won.")
        else:
            st.info("Upload participants first.")


def render_winner_board() -> None:
    if winner_board_placeholder is None:
        return

    with winner_board_placeholder.container():
        st.header("🏆 Winner Board")

        if st.session_state.winners:
            df_winners = pd.DataFrame(st.session_state.winners)
            df_winners.index = df_winners.index + 1
            df_winners.index.name = "No."
            st.dataframe(df_winners, use_container_width=True)

            csv_data = df_winners.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Winner Report",
                csv_data,
                "raffle_winners.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.info("No winners yet.")

if not event_mode:
    show_list = st.toggle("Show Participant List", value=True)

    if show_list:
        participant_placeholder = st.empty()
        render_participant_list()

    remaining_placeholder = st.empty()
    render_remaining_list()

# -------------------------
# Draw Area
# -------------------------
st.markdown('<div class="draw-title">🎯 DRAW AREA</div>', unsafe_allow_html=True)
draw_placeholder = st.empty()

# Fullscreen button lives in the main page
if event_mode:
    st.markdown('<div class="floating-draw-wrap">', unsafe_allow_html=True)
    start_draw = st.button("🎡 DRAW NOW", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    start_draw = st.sidebar.button("🎡 START RAFFLE DRAW", use_container_width=True)

# -------------------------
# Draw Logic
# -------------------------
if start_draw:
    available = get_remaining_participants()

    if not available:
        st.error("No eligible participants available.")
    elif len(available) < winner_count:
        st.error("Not enough participants remaining.")
    else:
        selected_winners = random.sample(available, winner_count)
        grid_class = get_grid_class(winner_count)

        # rolling animation
        delay = 0.015
        for _ in range(70):
            preview_names = random.sample(available, min(winner_count, len(available)))

            if winner_count == 1:
                draw_placeholder.markdown(
                    f"""
                    <div class="winner-box">
                        {preview_names[0]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                preview_html = "".join(
                    [f'<div class="multi-winner-item">{name}</div>' for name in preview_names]
                )

                draw_placeholder.markdown(
                    f"""
                    <div class="multi-winner-box">
                        <div class="multi-winner-title">
                            Drawing {winner_count} Winner(s)...
                        </div>
                        <div class="multi-winner-grid {grid_class}">
                            {preview_html}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            time.sleep(delay)
            delay += 0.0015

        # final winner display
        if winner_count == 1:
            winner_name = selected_winners[0]
            draw_placeholder.markdown(
                f"""
                <div class="winner-box">
                    🏆 {winner_name} 🏆
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            final_html = "".join(
                [f'<div class="multi-winner-item">🏆 {name}</div>' for name in selected_winners]
            )

            draw_placeholder.markdown(
                f"""
                <div class="multi-winner-box">
                    <div class="multi-winner-title">
                        WINNERS FOR: {prize}
                    </div>
                    <div class="multi-winner-grid {grid_class}">
                        {final_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        play_winner_sound("winner.m4a")
        st.balloons()

        # add winners one by one and update remaining list live
        for winner in selected_winners:
            st.session_state.winners.append({
                "Prize": prize,
                "Name": winner
            })

            if not event_mode and remaining_placeholder is not None:
                render_remaining_list()

        time.sleep(1)

# -------------------------
# Winner Board
# -------------------------
if not event_mode:
    winner_board_placeholder = st.empty()
    render_winner_board()
