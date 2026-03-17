import streamlit as st
import pandas as pd
import random
import time
import os
import base64
import streamlit.components.v1 as components

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="LMPC Raffle",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Constants
# -------------------------
ADMIN_PASSWORD = "lmpcadmin"  # change this before actual event
LOGO_FILE = "logo.png"
WINNER_SOUND_FILE = "winner.m4a"

# -------------------------
# Session State Defaults
# -------------------------
DEFAULTS = {
    "participants": [],
    "winners": [],
    "host_mode": False,
    "admin_authenticated": True,
    "prize": "Special Prize",
    "winner_count": 1,
    "show_participant_list": True,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------------
# Helpers
# -------------------------
def get_base64_image(image_path: str) -> str:
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def play_winner_sound(file_path: str) -> None:
    if not os.path.exists(file_path):
        return

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


def update_metrics() -> None:
    remaining = get_remaining_participants()
    participants_metric.metric("Participants", len(st.session_state.participants))
    winners_metric.metric("Winners", len(st.session_state.winners))
    remaining_metric.metric("Remaining Eligible", len(remaining))


def render_participant_list(placeholder) -> None:
    if placeholder is None:
        return

    with placeholder.container():
        st.subheader("Participant List")

        if st.session_state.participants:
            df_names = pd.DataFrame(st.session_state.participants, columns=["Name"])
            df_names.index = df_names.index + 1
            df_names.index.name = "No."
            st.dataframe(df_names, height=300, use_container_width=True)
        else:
            st.info("Upload an Excel file to display participants.")


def render_remaining_list(placeholder) -> None:
    if placeholder is None:
        return

    with placeholder.container():
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


def render_winner_board(placeholder) -> None:
    if placeholder is None:
        return

    with placeholder.container():
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


def enter_host_mode() -> None:
    st.session_state.host_mode = True
    st.session_state.admin_authenticated = False


def exit_host_mode() -> None:
    st.session_state.host_mode = False
    st.session_state.admin_authenticated = True


# -------------------------
# Sidebar / Admin Panel
# -------------------------
if not st.session_state.host_mode:
    st.sidebar.header("⚙️ Admin Panel")

    uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file is not None:
        try:
            st.session_state.participants = load_names_from_excel(uploaded_file)
            st.sidebar.success(f"{len(st.session_state.participants)} participants loaded")
        except Exception as e:
            st.sidebar.error(f"Failed to load participants: {e}")

    st.session_state.prize = st.sidebar.text_input("Prize Name", value=st.session_state.prize)
    st.session_state.winner_count = st.sidebar.number_input(
        "Number of Winners",
        min_value=1,
        value=int(st.session_state.winner_count),
        step=1
    )

    st.session_state.show_participant_list = st.sidebar.toggle(
        "Show Participant List",
        value=st.session_state.show_participant_list
    )

    col_admin_1, col_admin_2 = st.sidebar.columns(2)

    with col_admin_1:
        if st.button("🎤 Enter Host Mode", use_container_width=True):
            enter_host_mode()
            st.rerun()

    with col_admin_2:
        if st.button("🗑 Reset Winners", use_container_width=True):
            st.session_state.winners = []
            st.rerun()

    if st.sidebar.button("🧹 Clear Participants", use_container_width=True):
        st.session_state.participants = []
        st.session_state.winners = []
        st.rerun()

else:
    # Hide sidebar in host mode
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

.host-control-wrap{
    margin-top:0.5rem;
    margin-bottom:1rem;
}

.host-info-card{
    background:#f8f9fa;
    border:1px solid #dee2e6;
    border-radius:16px;
    padding:18px;
    height:100%;
}

.host-info-title{
    font-size:14px;
    color:#6c757d;
    margin-bottom:6px;
}

.host-info-value{
    font-size:26px;
    font-weight:800;
    color:#2c3e50;
    word-break:break-word;
}

.host-button button{
    font-size:28px !important;
    padding:18px 20px !important;
    border-radius:14px !important;
    font-weight:700 !important;
}

.admin-button button{
    font-size:18px !important;
    padding:14px 16px !important;
    border-radius:12px !important;
    font-weight:700 !important;
}
</style>
""", unsafe_allow_html=True)

if st.session_state.host_mode:
    st.markdown("""
    <style>
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
logo_b64 = get_base64_image(LOGO_FILE)
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
col1, col2, col3 = st.columns(3)
participants_metric = col1.empty()
winners_metric = col2.empty()
remaining_metric = col3.empty()
update_metrics()

# -------------------------
# Non-host mode tables
# -------------------------
participant_placeholder = None
remaining_placeholder = None
winner_board_placeholder = None

if not st.session_state.host_mode:
    if st.session_state.show_participant_list:
        participant_placeholder = st.empty()
        render_participant_list(participant_placeholder)

    remaining_placeholder = st.empty()
    render_remaining_list(remaining_placeholder)

# -------------------------
# Draw Area
# -------------------------
st.markdown('<div class="draw-title">🎯 DRAW AREA</div>', unsafe_allow_html=True)
draw_placeholder = st.empty()

# -------------------------
# Host / Draw Controls
# -------------------------
if st.session_state.host_mode:
    left, mid, right = st.columns([5, 2, 2])

    with left:
        st.markdown('<div class="host-button">', unsafe_allow_html=True)
        start_draw = st.button("🎡 DRAW NOW", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with mid:
        st.markdown(
            f"""
            <div class="host-info-card">
                <div class="host-info-title">Prize</div>
                <div class="host-info-value">{st.session_state.prize}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:
        st.markdown(
            f"""
            <div class="host-info-card">
                <div class="host-info-title">Possible Winners</div>
                <div class="host-info-value">{int(st.session_state.winner_count)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="host-control-wrap"></div>', unsafe_allow_html=True)

    admin_col_1, admin_col_2 = st.columns([8, 2])

    with admin_col_2:
        st.markdown('<div class="admin-button">', unsafe_allow_html=True)
        if st.button("⚙️ Admin Access", use_container_width=True):
            st.session_state.admin_authenticated = not st.session_state.admin_authenticated
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.admin_authenticated:
        with st.container():
            st.markdown("### Admin Unlock")
            password = st.text_input("Enter admin password", type="password", key="host_admin_password")
            col_exit_1, col_exit_2 = st.columns([3, 2])

            with col_exit_1:
                if st.button("❌ Exit Host Mode", use_container_width=True):
                    if password == ADMIN_PASSWORD:
                        exit_host_mode()
                        st.rerun()
                    else:
                        st.error("Incorrect password.")

            with col_exit_2:
                if st.button("🗑 Reset Winners", use_container_width=True):
                    if password == ADMIN_PASSWORD:
                        st.session_state.winners = []
                        st.rerun()
                    else:
                        st.error("Incorrect password.")
else:
    start_draw = st.sidebar.button("🎡 START RAFFLE DRAW", use_container_width=True)

# -------------------------
# Draw Logic
# -------------------------
if start_draw:
    available = get_remaining_participants()
    winner_count = int(st.session_state.winner_count)
    prize = st.session_state.prize

    if not available:
        st.error("No eligible participants available.")
    elif len(available) < winner_count:
        st.error("Not enough participants remaining.")
    else:
        selected_winners = random.sample(available, winner_count)
        grid_class = get_grid_class(winner_count)

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

        play_winner_sound(WINNER_SOUND_FILE)
        st.balloons()

        for winner in selected_winners:
            st.session_state.winners.append({
                "Prize": prize,
                "Name": winner
            })

            update_metrics()

            if not st.session_state.host_mode and remaining_placeholder is not None:
                render_remaining_list(remaining_placeholder)

            time.sleep(0.2)

# -------------------------
# Winner Board
# -------------------------
if not st.session_state.host_mode:
    winner_board_placeholder = st.empty()
    render_winner_board(winner_board_placeholder)
