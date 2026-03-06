import streamlit as st

# Title of the app
st.title('My First Streamlit App')

# Text input
name = st.text_input('Enter your name')

# Display the input
if name:
    st.write(f'Hello, {name}!')
else:
    st.write('Hello, World!')

# Button
if st.button('Click me'):
    st.write('You clicked the button!')