import streamlit as st
import pandas as pd
import secrets
import time
import os
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="LMPC Raffle", layout="wide")

# -------------------------
# Session Defaults
# -------------------------
if "participants" not in st.session_state:
    st.session_state.participants = []

if "winners" not in st.session_state:
    st.session_state.winners = []

if "host_mode" not in st.session_state:
    st.session_state.host_mode = False

if "prize" not in st.session_state:
    st.session_state.prize = "Special Prize"

if "winner_count" not in st.session_state:
    st.session_state.winner_count = 1


# -------------------------
# Helpers
# -------------------------
def get_base64_image(path: str) -> str:
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def play_winner_sound(path: str) -> None:
    if not os.path.exists(path):
        return

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    uid = str(time.time()).replace(".", "")

    html = f"""
    <audio id="a{uid}">
        <source src="data:audio/mp4;base64,{b64}" type="audio/mp4">
    </audio>
    <script>
    const a = document.getElementById("a{uid}");
    a.currentTime = 0;
    a.play().catch(() => null);
    </script>
    """

    components.html(html, height=0)


def load_names(file) -> list[str]:
    df = pd.read_excel(file, engine="openpyxl")
    names = (
        df.iloc[:, 0]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )
    return names


def remaining() -> list[str]:
    won = [w["Name"] for w in st.session_state.winners]
    return [p for p in st.session_state.participants if p not in won]


def grid(n: int) -> str:
    if n <= 6:
        return "cols-2"
    if n <= 12:
        return "cols-3"
    return "cols-4"


def secure_pick_winners(pool: list[str], count: int) -> list[str]:
    winners = []
    available = pool.copy()

    for _ in range(count):
        picked = secrets.choice(available)
        winners.append(picked)
        available.remove(picked)

    return winners


def secure_preview_sample(pool: list[str], count: int) -> list[str]:
    if not pool:
        return []
    return [secrets.choice(pool) for _ in range(count)]


# -------------------------
# Sidebar (ADMIN MODE)
# -------------------------
if not st.session_state.host_mode:
    st.sidebar.header("⚙️ Admin Panel")

    file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])

    if file:
        try:
            st.session_state.participants = load_names(file)
            st.sidebar.success(f"{len(st.session_state.participants)} loaded")
        except Exception as e:
            st.sidebar.error(f"Failed to load file: {e}")

    st.session_state.prize = st.sidebar.text_input("Prize", st.session_state.prize)

    st.session_state.winner_count = st.sidebar.number_input(
        "Winners",
        min_value=1,
        value=int(st.session_state.winner_count),
        step=1,
    )

    if st.sidebar.button("🎤 ENTER HOST MODE"):
        st.session_state.host_mode = True
        st.rerun()

    if st.sidebar.button("🗑 RESET WINNERS"):
        st.session_state.winners = []
        st.rerun()

else:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {display:none;}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------
# Styling
# -------------------------
st.markdown(
    """
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
    }

    .draw-title{
        text-align:center;
        font-size:30px;
        font-weight:800;
        color:#ff4b4b;
        margin-top:10px;
    }

    .winner-box{
        background:#111;
        padding:80px;
        border-radius:20px;
        text-align:center;
        font-size:90px;
        color:gold;
        font-weight:800;
        word-wrap:break-word;
    }

    .multi-winner-box{
        background:#111;
        padding:40px;
        border-radius:20px;
        color:white;
    }

    .multi-winner-grid{
        display:grid;
        gap:16px;
    }

    .cols-2{grid-template-columns:repeat(2,1fr);}
    .cols-3{grid-template-columns:repeat(3,1fr);}
    .cols-4{grid-template-columns:repeat(4,1fr);}

    .multi-winner-item{
        background:#1c1c1c;
        border:2px solid gold;
        border-radius:14px;
        padding:16px;
        text-align:center;
        font-size:28px;
        color:gold;
        font-weight:700;
        word-wrap:break-word;
    }

    .draw-button-wrap button {
        font-size:36px !important;
        padding:26px !important;
        border-radius:16px !important;
        font-weight:800 !important;
        background:linear-gradient(135deg,#ff4b4b,#ff7a18) !important;
        color:white !important;
        border:none !important;
        box-shadow:0 10px 25px rgba(0,0,0,0.25) !important;
        min-height:88px !important;
    }

    .back-button-wrap button {
        font-size:18px !important;
        padding:14px !important;
        border-radius:12px !important;
        font-weight:700 !important;
        min-height:52px !important;
    }

    .info-card{
        background:#f8f9fa;
        padding:16px;
        border-radius:14px;
        border:1px solid #e5e7eb;
        height:100%;
    }

    .info-label{
        font-size:14px;
        color:#6b7280;
        margin-bottom:6px;
    }

    .logo-wrap{
        text-align:center;
        margin-bottom:8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------
# Header
# -------------------------
logo = get_base64_image("logo.png")
if logo:
    st.markdown(
        f'<div class="logo-wrap"><img src="data:image/png;base64,{logo}" width="140"></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="main-title">LODLOD MULTI-PURPOSE COOPERATIVE</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">🎉 LIVE RAFFLE DRAW SYSTEM 🎉</div>',
    unsafe_allow_html=True,
)

st.divider()


# -------------------------
# Metrics
# -------------------------
c1, c2, c3 = st.columns(3)
m1 = c1.empty()
m2 = c2.empty()
m3 = c3.empty()


def refresh() -> None:
    m1.metric("Participants", len(st.session_state.participants))
    m2.metric("Winners", len(st.session_state.winners))
    m3.metric("Remaining", len(remaining()))


refresh()


# -------------------------
# DRAW AREA
# -------------------------
st.markdown('<div class="draw-title">🎯 DRAW AREA</div>', unsafe_allow_html=True)
draw = st.empty()


# -------------------------
# HOST MODE UI
# -------------------------
if st.session_state.host_mode:
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("#### 🎁 Prize")
        st.session_state.prize = st.text_input(
            "",
            value=st.session_state.prize,
            key="host_prize_input",
            label_visibility="collapsed",
        )

    with col2:
        st.markdown("#### 🏆 Number of Winners")
        st.session_state.winner_count = st.number_input(
            "",
            min_value=1,
            value=int(st.session_state.winner_count),
            step=1,
            key="host_winner_input",
            label_visibility="collapsed",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    left, center, right = st.columns([2, 4, 2])

    with center:
        st.markdown('<div class="draw-button-wrap">', unsafe_allow_html=True)
        start = st.button("🎡 DRAW NOW", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    info_left, info_mid, info_right = st.columns([2, 3, 2])

    with info_mid:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Current Prize</div>
                <div style="font-size:26px;font-weight:800;color:#2c3e50;">{st.session_state.prize}</div>
                <div style="margin-top:12px;" class="info-label">Possible Winners</div>
                <div style="font-size:26px;font-weight:800;color:#2c3e50;">{int(st.session_state.winner_count)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    exit_l, exit_c, exit_r = st.columns([3, 2, 3])

    with exit_c:
        st.markdown('<div class="back-button-wrap">', unsafe_allow_html=True)
        if st.button("⚙️ BACK TO ADMIN", use_container_width=True):
            st.session_state.host_mode = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    start = st.sidebar.button("🎡 START DRAW")


# -------------------------
# DRAW LOGIC
# -------------------------
if start:
    avail = remaining()
    requested_winners = int(st.session_state.winner_count)

    if len(avail) < requested_winners:
        st.error("Not enough participants")
    else:
        winners = secure_pick_winners(avail, requested_winners)
        cls = grid(len(winners))

        # animation
        for _ in range(60):
            sample = secure_preview_sample(avail, min(len(winners), len(avail)))

            if len(winners) == 1:
                draw.markdown(
                    f'<div class="winner-box">{sample[0]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                html = "".join(
                    [f'<div class="multi-winner-item">{n}</div>' for n in sample]
                )
                draw.markdown(
                    f'<div class="multi-winner-box"><div class="multi-winner-grid {cls}">{html}</div></div>',
                    unsafe_allow_html=True,
                )

            time.sleep(0.02)

        # final
        if len(winners) == 1:
            draw.markdown(
                f'<div class="winner-box">🏆 {winners[0]} 🏆</div>',
                unsafe_allow_html=True,
            )
        else:
            html = "".join(
                [f'<div class="multi-winner-item">🏆 {n}</div>' for n in winners]
            )
            draw.markdown(
                f'<div class="multi-winner-box"><div class="multi-winner-grid {cls}">{html}</div></div>',
                unsafe_allow_html=True,
            )

        play_winner_sound("winner.m4a")
        st.balloons()

        for w in winners:
            st.session_state.winners.append(
                {"Prize": st.session_state.prize, "Name": w}
            )
            refresh()
            time.sleep(0.2)


# -------------------------
# ADMIN TABLES
# -------------------------
if not st.session_state.host_mode:
    st.subheader("Participants")
    if st.session_state.participants:
        df = pd.DataFrame(st.session_state.participants, columns=["Name"])
        df.index += 1
        df.index.name = "No."
        st.dataframe(df, height=300, use_container_width=True)

    st.subheader("Remaining Eligible Participants")
    rem = remaining()
    if rem:
        df = pd.DataFrame(rem, columns=["Name"])
        df.index += 1
        df.index.name = "No."
        st.dataframe(df, height=300, use_container_width=True)
    elif st.session_state.participants:
        st.success("All participants have already won.")

    st.subheader("Winners")
    if st.session_state.winners:
        df = pd.DataFrame(st.session_state.winners)
        df.index += 1
        df.index.name = "No."
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode(),
            "winners.csv",
            "text/csv",
        )
