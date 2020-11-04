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
        "On this page you can find information about how to use the Collect JD Details tab of the nugget JD API Demo "
        "Environment. "
        "You will be presented with a textbox. Depending on your need you will either be pasting in a url "
        "to a job site or the text of a job description. Your text box will look like the text below")
    text = st.text_area("This is your text box ", value="Your URL or Job text goes here")
    st.subheader("You specify your input by using the checkbox for the app. This demo environment makes it very easy to"
                 "test out the functionality of the API.  ")
    st.header("Accessing the API in your own Code")
    st.subheader(
        "The api sends and receives information through http get requests in json format. The syntax for sending"
        "a request to the collect JD details route is as follows:")
    st.code('''
    url = '<string: your url>'
    is_text = '<bool: is the url item plaintext of a web URL >'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"url": url, "is_text": is_text}) #convert the diction
    response = requests.get("<api-endpoint/>", headers=headers, data=data)
    response_dict = json.loads(response.json()) # get the response object back as a dictionary
    ''', language="python")

    st.subheader("The response object you get back will look like this")
    st.json('''
    {
    "category": "",
    "certification": [],
    "company": "",
    "company_size": "",
    "description": "",
    "education": [],
    "employment_type": [],
    "functions": [],
    "industry": [],
    "job_level": [],
    "language": [],
    "location": "",
    "major": [],
    "other_experience": [],
    "salary_high": "",
    "salary_low": "",
    "salary_source": "",
    "tasks": [],
    "title": "",
    "tools": [],
    "url": "",
    "volunteering": []
}
    ''')
