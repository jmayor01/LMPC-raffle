import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Raffle Draw System", layout="wide")

st.title("🎉 Raffle Draw System")

# Session state storage
if "participants" not in st.session_state:
    st.session_state.participants = []

if "winners" not in st.session_state:
    st.session_state.winners = []

# Upload participant file
st.sidebar.header("Upload Participants")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel File", type=["xlsx"]
)

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean names (first column only)
    names = df.iloc[:, 0].dropna().astype(str).tolist()

    st.session_state.participants = names

    st.success(f"{len(names)} participants loaded.")

# Display participants
if st.session_state.participants:
    st.subheader("Participants")
    st.dataframe(st.session_state.participants)

# Prize setup
st.sidebar.header("Prize Setup")

prize_name = st.sidebar.text_input("Prize Name")

winner_count = st.sidebar.number_input(
    "Number of Winners",
    min_value=1,
    step=1
)

allow_repeat = st.sidebar.checkbox("Allow previous winners to win again")

# Draw button
if st.sidebar.button("🎲 Draw Winners"):

    participants = st.session_state.participants

    if not allow_repeat:
        previous_winners = [w["Name"] for w in st.session_state.winners]
        participants = [p for p in participants if p not in previous_winners]

    if winner_count > len(participants):
        st.error("Not enough participants left.")
    else:

        selected = random.sample(participants, winner_count)

        for name in selected:
            st.session_state.winners.append({
                "Prize": prize_name,
                "Name": name
            })

# Display winners
st.subheader("🏆 Winners")

if st.session_state.winners:
    winners_df = pd.DataFrame(st.session_state.winners)
    st.dataframe(winners_df)

    # Export report
    csv = winners_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Winners Report",
        csv,
        "raffle_winners.csv",
        "text/csv"
    )

else:
    st.info("No winners drawn yet.")
