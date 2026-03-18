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
def get_base64_image(path):
    if os.path.exists(path):
        return base64.b64encode(open(path, "rb").read()).decode()
    return ""

def play_winner_sound(path):
    if not os.path.exists(path):
        return

    b64 = base64.b64encode(open(path, "rb").read()).decode()
    uid = str(time.time()).replace(".", "")

    components.html(f"""
    <audio id="a{uid}">
        <source src="data:audio/mp4;base64,{b64}" type="audio/mp4">
    </audio>
    <script>
    var a = document.getElementById("a{uid}");
    a.currentTime = 0;
    a.play().catch(()=>null);
    </script>
    """, height=0)

def load_names(file):
    df = pd.read_excel(file, engine="openpyxl")
    return (
        df.iloc[:,0]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )

def remaining():
    won = [w["Name"] for w in st.session_state.winners]
    return [p for p in st.session_state.participants if p not in won]

def grid(n):
    if n <= 6: return "cols-2"
    if n <= 12: return "cols-3"
    return "cols-4"

def refresh():
    m1.metric("Participants", len(st.session_state.participants))
    m2.metric("Winners", len(st.session_state.winners))
    m3.metric("Remaining", len(remaining()))

# -------------------------
# Sidebar (ADMIN)
# -------------------------
if not st.session_state.host_mode:

    st.sidebar.header("⚙️ Admin Panel")

    file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])

    if file:
        st.session_state.participants = load_names(file)
        st.sidebar.success(f"{len(st.session_state.participants)} loaded")

    st.session_state.prize = st.sidebar.text_input("Prize", st.session_state.prize)

    st.session_state.winner_count = st.sidebar.number_input(
        "Winners",
        min_value=1,
        value=int(st.session_state.winner_count)
    )

    if st.sidebar.button("🎤 ENTER HOST MODE"):
        st.session_state.host_mode = True
        st.rerun()

    if st.sidebar.button("🗑 RESET WINNERS"):
        st.session_state.winners = []
        st.rerun()

else:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# Styling
# -------------------------
st.markdown("""
<style>
.main-title{text-align:center;font-size:42px;font-weight:800;color:#2c3e50;}
.sub-title{text-align:center;font-size:22px;color:#6c757d;}
.draw-title{text-align:center;font-size:30px;font-weight:800;color:#ff4b4b;}

.winner-box{
background:#111;padding:80px;border-radius:20px;
text-align:center;font-size:90px;color:gold;font-weight:800;
}

.multi-winner-box{
background:#111;padding:40px;border-radius:20px;color:white;
}

.multi-winner-grid{display:grid;gap:16px;}
.cols-2{grid-template-columns:repeat(2,1fr);}
.cols-3{grid-template-columns:repeat(3,1fr);}
.cols-4{grid-template-columns:repeat(4,1fr);}

.multi-winner-item{
background:#1c1c1c;border:2px solid gold;border-radius:14px;
padding:16px;text-align:center;font-size:28px;color:gold;
}

.draw-button-wrap button{
font-size:36px !important;
padding:26px !important;
border-radius:16px !important;
font-weight:800 !important;
background:linear-gradient(135deg,#ff4b4b,#ff7a18) !important;
color:white !important;
min-height:90px !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Header
# -------------------------
logo = get_base64_image("logo.png")
if logo:
    st.markdown(f'<div style="text-align:center"><img src="data:image/png;base64,{logo}" width="140"></div>', unsafe_allow_html=True)

st.markdown('<div class="main-title">LODLOD MULTI-PURPOSE COOPERATIVE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🎉 LIVE RAFFLE DRAW SYSTEM 🎉</div>', unsafe_allow_html=True)

st.divider()

# -------------------------
# Metrics
# -------------------------
c1,c2,c3 = st.columns(3)
m1 = c1.empty()
m2 = c2.empty()
m3 = c3.empty()

refresh()

# -------------------------
# Draw Area
# -------------------------
st.markdown('<div class="draw-title">🎯 DRAW AREA</div>', unsafe_allow_html=True)
draw = st.empty()

# -------------------------
# HOST MODE UI
# -------------------------
if st.session_state.host_mode:

    col1, col2 = st.columns([3,2])

    with col1:
        st.markdown("#### 🎁 Prize")
        st.session_state.prize = st.text_input("", st.session_state.prize)

    with col2:
        st.markdown("#### 🏆 Winners")
        st.session_state.winner_count = st.number_input(
            "", min_value=1, value=int(st.session_state.winner_count)
        )

    st.markdown("<br>", unsafe_allow_html=True)

    _, center, _ = st.columns([2,4,2])

    with center:
        st.markdown('<div class="draw-button-wrap">', unsafe_allow_html=True)
        start = st.button("🎡 DRAW NOW", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("⚙️ BACK TO ADMIN"):
        st.session_state.host_mode = False
        st.rerun()

else:
    start = st.sidebar.button("🎡 START DRAW")

# -------------------------
# DRAW LOGIC (FAST)
# -------------------------
if start:

    avail = remaining()
    count = int(st.session_state.winner_count)

    if len(avail) < count:
        st.error("Not enough participants")
    else:

        # secure picks
        winners = []
        pool = avail.copy()

        for _ in range(count):
            pick = secrets.choice(pool)
            winners.append(pick)
            pool.remove(pick)

        cls = grid(len(winners))

        # animation
        for _ in range(50):
            sample = [secrets.choice(avail) for _ in range(min(len(winners), len(avail)))]

            if len(winners) == 1:
                draw.markdown(f'<div class="winner-box">{sample[0]}</div>', unsafe_allow_html=True)
            else:
                html = "".join([f'<div class="multi-winner-item">{n}</div>' for n in sample])
                draw.markdown(f'<div class="multi-winner-box"><div class="multi-winner-grid {cls}">{html}</div></div>', unsafe_allow_html=True)

            time.sleep(0.015)

        # final display
        if len(winners) == 1:
            draw.markdown(f'<div class="winner-box">🏆 {winners[0]} 🏆</div>', unsafe_allow_html=True)
        else:
            html = "".join([f'<div class="multi-winner-item">🏆 {n}</div>' for n in winners])
            draw.markdown(f'<div class="multi-winner-box"><div class="multi-winner-grid {cls}">{html}</div></div>', unsafe_allow_html=True)

        play_winner_sound("winner.m4a")
        st.balloons()

        # ⚡ batch update (FAST FIX)
        st.session_state.winners.extend([
            {"Prize": st.session_state.prize, "Name": w}
            for w in winners
        ])

        refresh()

# -------------------------
# Admin Tables
# -------------------------
if not st.session_state.host_mode:

    st.subheader("Participants")
    if st.session_state.participants:
        df = pd.DataFrame(st.session_state.participants, columns=["Name"])
        df.index += 1
        st.dataframe(df, height=300)

    st.subheader("Remaining")
    rem = remaining()
    if rem:
        df = pd.DataFrame(rem, columns=["Name"])
        df.index += 1
        st.dataframe(df, height=300)

    st.subheader("Winners")
    if st.session_state.winners:
        df = pd.DataFrame(st.session_state.winners)
        df.index += 1
        st.dataframe(df)

        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode(),
            "winners.csv"
        )
