import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Raffle Draw System", page_icon="🎉", layout="wide")

st.title("🎉 LMPC Raffle Draw System")

st.markdown("Upload participants and draw winners for each prize category.")

# Upload participants
uploaded_file = st.file_uploader("Upload Participants (CSV or Excel)", type=["csv", "xlsx"])

participants = []

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    participants = df.iloc[:,0].dropna().tolist()

    st.success(f"Total Participants: {len(participants)}")

else:
    st.warning("Upload a participants file to start.")


st.divider()

# Prize categories
st.subheader("🏆 Prize Categories")

grand = st.number_input("Grand Prize Winners", min_value=0, value=1)
second = st.number_input("Second Prize Winners", min_value=0, value=2)
third = st.number_input("Third Prize Winners", min_value=0, value=3)

if "remaining" not in st.session_state:
    st.session_state.remaining = []

if participants and not st.session_state.remaining:
    st.session_state.remaining = participants.copy()


def draw_winners(num):
    winners = random.sample(st.session_state.remaining, num)
    for w in winners:
        st.session_state.remaining.remove(w)
    return winners


st.divider()

if st.button("🎲 Start Raffle Draw"):

    results = {}

    if grand > 0:
        st.subheader("🏆 Grand Prize Draw")
        time.sleep(1)
        winners = draw_winners(grand)
        results["Grand Prize"] = winners

        for w in winners:
            st.write("🎉", w)
        st.balloons()

    if second > 0:
        st.subheader("🥈 Second Prize Draw")
        time.sleep(1)
        winners = draw_winners(second)
        results["Second Prize"] = winners

        for w in winners:
            st.write("🎉", w)

    if third > 0:
        st.subheader("🥉 Third Prize Draw")
        time.sleep(1)
        winners = draw_winners(third)
        results["Third Prize"] = winners

        for w in winners:
            st.write("🎉", w)

    # Save winners
    data = []

    for prize, winners in results.items():
        for w in winners:
            data.append({
                "Prize": prize,
                "Winner": w
            })

    winners_df = pd.DataFrame(data)

    st.divider()

    st.subheader("📄 Download Winners")

    st.download_button(
        "Download Winners CSV",
        winners_df.to_csv(index=False),
        "raffle_winners.csv",
        "text/csv"
    )
