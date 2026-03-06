import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Raffle Roulette", layout="wide")

st.title("🎉 Raffle Roulette Draw")

# session storage
if "participants" not in st.session_state:
    st.session_state.participants = []

if "winners" not in st.session_state:
    st.session_state.winners = []

# Upload file
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    names = df.iloc[:,0].dropna().astype(str).tolist()

    st.session_state.participants = names

    st.success(f"{len(names)} participants loaded")

# show participants
if st.session_state.participants:
    st.subheader("Participants")
    st.write(f"Total Participants: {len(st.session_state.participants)}")

# prize configuration
st.sidebar.header("Prize Settings")

prize_name = st.sidebar.text_input("Prize Name")

winner_count = st.sidebar.number_input(
    "Number of Winners",
    min_value=1,
    value=1
)

allow_repeat = st.sidebar.checkbox("Allow repeat winners")

draw_button = st.sidebar.button("🎡 Start Roulette Draw")

roulette_display = st.empty()

if draw_button:

    available = st.session_state.participants

    if not allow_repeat:
        previous = [w["Name"] for w in st.session_state.winners]
        available = [p for p in available if p not in previous]

    if len(available) < winner_count:
        st.error("Not enough participants remaining.")
    else:

        winners = []

        for i in range(winner_count):

            # roulette animation
            for _ in range(40):
                name = random.choice(available)
                roulette_display.markdown(
                    f"<h1 style='text-align:center;color:red'>{name}</h1>",
                    unsafe_allow_html=True
                )
                time.sleep(0.05)

            selected = random.choice(available)

            roulette_display.markdown(
                f"<h1 style='text-align:center;color:green'>🏆 {selected}</h1>",
                unsafe_allow_html=True
            )

            winners.append(selected)
            available.remove(selected)

            time.sleep(2)

        for w in winners:
            st.session_state.winners.append({
                "Prize": prize_name,
                "Name": w
            })

# winners table
st.subheader("🏆 Winners")

if st.session_state.winners:

    df_winners = pd.DataFrame(st.session_state.winners)

    st.dataframe(df_winners)

    csv = df_winners.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Winners Report",
        csv,
        "raffle_winners.csv",
        "text/csv"
    )
