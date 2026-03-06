import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import time
import os
import base64

st.set_page_config(page_title="LMPC Raffle", layout="wide")

# -------------------------
# Helpers
# -------------------------
def get_base64_image(image_path: str) -> str:
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def load_names_from_excel(uploaded_file) -> list[str]:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    names = df.iloc[:, 0].dropna().astype(str).str.strip()
    names = names[names != ""].drop_duplicates().tolist()
    return names

def spin_wheel_html(names: list[str], winner: str) -> str:
    safe_names = [str(n).replace("'", "\\'") for n in names]
    labels_js = ", ".join([f"'{n}'" for n in safe_names])
    winner_js = winner.replace("'", "\\'")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{
          margin: 0;
          background: transparent;
          font-family: Arial, sans-serif;
          color: white;
          text-align: center;
        }}

        .wrap {{
          display: flex;
          justify-content: center;
          align-items: center;
          flex-direction: column;
          padding-top: 10px;
        }}

        .wheel-container {{
          position: relative;
          width: 560px;
          height: 560px;
          margin: 0 auto;
        }}

        .pointer {{
          position: absolute;
          top: -8px;
          left: 50%;
          transform: translateX(-50%);
          width: 0;
          height: 0;
          border-left: 24px solid transparent;
          border-right: 24px solid transparent;
          border-top: 0;
          border-bottom: 42px solid #ff4b4b;
          z-index: 10;
          filter: drop-shadow(0 3px 6px rgba(0,0,0,0.35));
        }}

        canvas {{
          border-radius: 50%;
          background: #ffffff;
          box-shadow: 0 10px 35px rgba(0,0,0,0.25);
        }}

        .caption {{
          margin-top: 18px;
          font-size: 20px;
          font-weight: bold;
          color: #2c3e50;
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="wheel-container">
          <div class="pointer"></div>
          <canvas id="wheel" width="560" height="560"></canvas>
        </div>
        <div class="caption">Spinning wheel raffle in progress...</div>
      </div>

      <script>
        const names = [{labels_js}];
        const winner = '{winner_js}';
        const canvas = document.getElementById("wheel");
        const ctx = canvas.getContext("2d");

        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 250;
        const sliceAngle = (Math.PI * 2) / names.length;

        const colors = [
          "#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
          "#59a14f", "#edc948", "#b07aa1", "#ff9da7",
          "#9c755f", "#bab0ab", "#3b82f6", "#10b981"
        ];

        let currentRotation = 0;

        function drawWheel(rotation = 0) {{
          ctx.clearRect(0, 0, canvas.width, canvas.height);

          for (let i = 0; i < names.length; i++) {{
            const start = rotation + i * sliceAngle - Math.PI / 2;
            const end = start + sliceAngle;

            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, start, end);
            ctx.closePath();
            ctx.fillStyle = colors[i % colors.length];
            ctx.fill();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(start + sliceAngle / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 14px Arial";

            let label = names[i];
            if (label.length > 18) {{
              label = label.substring(0, 18) + "...";
            }}

            ctx.fillText(label, radius - 18, 5);
            ctx.restore();
          }}

          // center circle
          ctx.beginPath();
          ctx.arc(centerX, centerY, 55, 0, Math.PI * 2);
          ctx.fillStyle = "#2c3e50";
          ctx.fill();
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 5;
          ctx.stroke();

          ctx.fillStyle = "#ffffff";
          ctx.font = "bold 18px Arial";
          ctx.textAlign = "center";
          ctx.fillText("RAFFLE", centerX, centerY + 6);
        }}

        function getWinnerIndex() {{
          return names.findIndex(n => n === winner);
        }}

        function spinToWinner() {{
          const winnerIndex = getWinnerIndex();

          // Pointer is at top. We want the winner slice centered at top.
          const targetSliceCenter = winnerIndex * sliceAngle + sliceAngle / 2;
          const targetRotation = (Math.PI * 2 * 8) + (Math.PI * 2 - targetSliceCenter);

          const duration = 6500;
          const startTime = performance.now();

          function easeOutCubic(t) {{
            return 1 - Math.pow(1 - t, 3);
          }}

          function animate(now) {{
            const elapsed = now - startTime;
            const t = Math.min(elapsed / duration, 1);
            const eased = easeOutCubic(t);

            currentRotation = targetRotation * eased;
            drawWheel(currentRotation);

            if (t < 1) {{
              requestAnimationFrame(animate);
            }} else {{
              drawWheel(targetRotation);
            }}
          }}

          requestAnimationFrame(animate);
        }}

        drawWheel(0);
        setTimeout(spinToWinner, 500);
      </script>
    </body>
    </html>
    """

# -------------------------
# Session state
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
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    color: #2c3e50;
    margin-bottom: 0;
}

.sub-title {
    text-align: center;
    font-size: 22px;
    color: #6c757d;
    margin-top: 0.2rem;
    margin-bottom: 1rem;
}

.draw-title {
    text-align: center;
    font-size: 28px;
    font-weight: 800;
    color: #ff4b4b;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

.winner-box {
    text-align: center;
    padding: 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, #fff8e1, #fff3cd);
    border: 2px solid #f4c542;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    margin-top: 12px;
}

.winner-name {
    font-size: 42px;
    font-weight: 900;
    color: #c0392b;
}

.small-note {
    text-align:center;
    color:#6c757d;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Centered logo
# -------------------------
logo_b64 = get_base64_image("logo.png")
if logo_b64:
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:6px;">
            <img src="data:image/png;base64,{logo_b64}" width="150">
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('<div class="main-title">LODLOD MULTI-PURPOSE COOPERATIVE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🎉 LIVE RAFFLE DRAW SYSTEM 🎉</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Transparent spinning wheel selection for live presentation</div>', unsafe_allow_html=True)

st.divider()

# -------------------------
# Sidebar
# -------------------------
st.sidebar.header("Upload Participants")
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    try:
        st.session_state.participants = load_names_from_excel(uploaded_file)
        st.sidebar.success(f"Loaded {len(st.session_state.participants)} participants.")
    except Exception as e:
        st.sidebar.error(f"Failed to read Excel file: {e}")

st.sidebar.header("Prize Setup")
prize = st.sidebar.text_input("Prize Name", value="Special Prize")
winner_count = st.sidebar.number_input("Number of Winners", min_value=1, value=1, step=1)
start_draw = st.sidebar.button("🎡 START SPINNING WHEEL", use_container_width=True)

# -------------------------
# Metrics
# -------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Participants", len(st.session_state.participants))
with col2:
    st.metric("Winners", len(st.session_state.winners))
with col3:
    previous_winner_names = [w["Name"] for w in st.session_state.winners]
    remaining = len([p for p in st.session_state.participants if p not in previous_winner_names])
    st.metric("Remaining Eligible", remaining)

# -------------------------
# Participant list visible by default
# -------------------------
show_list = st.toggle("Show Participant List", value=True)

if show_list:
    st.subheader("Participant List")
    if st.session_state.participants:
        df_names = pd.DataFrame(st.session_state.participants, columns=["Name"])
        st.dataframe(df_names, use_container_width=True, height=320)
    else:
        st.info("Upload an Excel file to display participants.")

# -------------------------
# Draw area
# -------------------------
st.markdown('<div class="draw-title">🎯 WINNER DRAW AREA</div>', unsafe_allow_html=True)
wheel_placeholder = st.empty()
winner_placeholder = st.empty()

# -------------------------
# Draw logic
# -------------------------
if start_draw:
    if not st.session_state.participants:
        st.error("Please upload the participant Excel file first.")
    else:
        previous_winner_names = [w["Name"] for w in st.session_state.winners]
        available = [p for p in st.session_state.participants if p not in previous_winner_names]

        if len(available) < winner_count:
            st.error("Not enough participants remaining for the requested number of winners.")
        else:
            drawn_winners = []

            for draw_no in range(winner_count):
                winner = random.choice(available)

                wheel_placeholder.components.v1.html(
                    spin_wheel_html(available, winner),
                    height=700,
                    scrolling=False
                )

                time.sleep(7)

                winner_placeholder.markdown(
                    f"""
                    <div class="winner-box">
                        <div style="font-size:18px; color:#7f8c8d; font-weight:700;">
                            WINNER FOR: {prize}
                        </div>
                        <div class="winner-name">🏆 {winner} 🏆</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.balloons()
                drawn_winners.append(winner)
                available.remove(winner)

                st.session_state.winners.append({
                    "Prize": prize,
                    "Name": winner
                })

# -------------------------
# Winner board
# -------------------------
st.header("🏆 Winner Board")

if st.session_state.winners:
    df_winners = pd.DataFrame(st.session_state.winners)
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
