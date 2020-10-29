import streamlit as st

st.title("nugget.ai JD API Documentation")
st.sidebar.title("API Reference")
st.sidebar.text("Reference Guides")
app_mode = st.sidebar.radio(
    "Select a Route", ["Collect JD details", "Show named entities", "Show JD similarity",
                       "Visualize NER training data", "Get years of experience"])

if app_mode == "Collect JD details":
    st.header("Collecting Job Description Details")
    st.subheader(
        "On this page you can find information about how to use the Collect JD Details tab of the nugget JD API."
        "You will be presented with a textbox. Depending on your need you will either be pasting in a url "
        "to a job site or the text of a job description. Your text box will look like the text below")
    text = st.text_area("This is your text box ", value="Your URL or Job text goes here")
    st.subheader("You specify your input by")
