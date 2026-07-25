import streamlit as st
import pandas as pd


def get_letter_grade(mark: float) -> str:
    if 90 <= mark <= 100:
        return "A"
    if 80 <= mark <= 89:
        return "B"
    if 70 <= mark <= 79:
        return "C"
    if 60 <= mark <= 69:
        return "D"
    return "E"


st.set_page_config(page_title="Subject Grade Dashboard", page_icon="📚", layout="centered")
st.title("Subject Grade Dashboard")
st.write("Enter marks for five subjects and view the results in a table and chart.")

subjects = ["Math", "Science", "English", "History", "Computer"]

with st.form("grade_form"):
    values = []
    for subject in subjects:
        raw_value = st.text_input(f"{subject} mark", placeholder="0-100")
        values.append(raw_value)

    submitted = st.form_submit_button("Calculate grades")

if submitted:
    rows = []
    valid = True
    for subject, raw_value in zip(subjects, values):
        if raw_value.strip() == "":
            st.error(f"Please enter a mark for {subject}.")
            valid = False
            break
        if not raw_value.replace(".", "", 1).isdigit():
            st.error(f"Please enter a valid number for {subject}.")
            valid = False
            break
        mark = float(raw_value)
        if mark < 0 or mark > 100:
            st.error(f"Please enter a mark between 0 and 100 for {subject}.")
            valid = False
            break
        rows.append({"Subject": subject, "Mark": mark, "Grade": get_letter_grade(mark)})

    if valid:
        df = pd.DataFrame(rows)
        st.success("Results")
        st.dataframe(df, use_container_width=True)

        st.bar_chart(df.set_index("Subject")["Mark"])

        average_mark = df["Mark"].mean()
        highest_mark = df.loc[df["Mark"].idxmax()]
        st.subheader("Summary")
        st.metric("Average mark", f"{average_mark:.1f}")
        st.metric("Top subject", f"{highest_mark['Subject']} ({highest_mark['Mark']})")
