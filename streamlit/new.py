import streamlit as st

# Text & Headers

st.header("This is a header")
st.subheader("This is a subheader")
st.text("This is some regular text.")
st.markdown("This is **Markdown** text with *italic* and **bold** formatting.")
#st.snow()
#st.balloons()
st.toast("This is a toast notification!", icon="🎉" )
if st.selectbox("Choose an option:", ["Option 1", "Option 2", "Option 3"]) == "Option 1":
    st.write("You selected Option 1!")

#name2 = st.text_input("Enter your name:")
#st.text_area("Enter your message:")



# st.caption("This is a caption text.")
# st.code("print('Hello, Streamlit!')", language='python')
# st.json({"name": "Streamlit", "type": "library", "language": "Python"})
# st.latex(r"E = mc^2")
# st.write("This is a versatile write function that can display text, data, and more.")
# st.title("This is a title")
st.success("This is a success message.")
st.info("This is an info message.")
st.warning("This is a warning message.")
# st.error("This is an error message.")
# st.exception("This is an exception message.")
st.metric("Temperature", "25 °C", "+1.5 °C")
# st.balloons()
# st.snow()
# st.toast("This is a toast notification!", icon="🎉")
st.progress(0.5)

# Buttons

if st.button("Click Me"):
  st.error("Button clicked!")

# Sliders & Inputs

name1 = st.text_input("Enter your name:")
age1 = st.slider("Select Age", 1, 100, 25)

if st.button("Submit"):
    st.write(f"Hello, {name1}! You are {age1} years old.")

# File Uploader

uploaded_file = st.file_uploader("Choose a file", type=["txt", "csv", "xlsx"])
if uploaded_file is not None:
    st.write("File uploaded successfully!")
    st.write(uploaded_file.name)
    st.write(uploaded_file.size)
    st.write(uploaded_file.type)
    import pandas as pd
    df = pd.read_csv(uploaded_file)
    st.write(df)
    