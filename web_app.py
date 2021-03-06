import io
import json
import string
from ast import literal_eval

import jsonlines
import nltk
import pandas as pd
import requests
import streamlit as st
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import SessionState

base_url = 'https://ry5tpjc0ci.execute-api.us-east-2.amazonaws.com/production'
nltk.download('stopwords')
nltk.download('wordnet')

# here we are using streamlit to enable a webapp for the API
st.title("JD Algorithm")
st.sidebar.title("Menu Select")
st.set_option('deprecation.showfileUploaderEncoding', False)
# This lets us select different screens in streamlits sidebar
app_mode = st.sidebar.radio("Choose the app mode",
                            ["Collect JD details", "Show JD similarity",
                             "Visualize NER training data"])
api_key = st.sidebar.text_input("Please input your API key")
session_state = SessionState.get(data=None, col_list=[], file_obj=None, reader=None)


def rename(name):
    return name.replace(" ", "_").lower()


def remap(key):
    remap_dict = {"jd-group-1": "batch", "jd-group-2": "batch", "resume-batch1": "batch"}
    return remap_dict[key] if key in remap_dict.keys() else key


if app_mode == "Collect JD details":
    # we grab a url from the user and send it by http request to the endpoint we want
    st.header("Collect Job Description Information")
    st.subheader("""
                    This route is for collecting information related to a given job description.
    
                    It can give you general information such as the title of the job and the company as well as more unique insights
                    such as what soft skills are relevant to the job and where are they present in the text as well as the years of experience certain skills require.
                    To use the API 
                    
                    -   paste in either a URL or a plaintext job description. Only 1 at a time, if both are inputted the app will default to using the url.
                    
                    -   Use the checkboxes to indicate what information you want to get 
                    from the API and then send it off!"""
                 )

    url = st.text_input("if your input is a url, please input a url")
    text = st.text_area("If your input is plaintext, please input plaintext")
    ent = st.checkbox("Would you like to see soft skills labeled?")
    exp = st.checkbox("Would you like to see years of experience labeled?")
    req = st.checkbox("Would you like to see required and desired features?")
    headers = {'Content-Type': 'application/json', 'x-api-key': api_key}
    if url:
        data = json.dumps({"url": url, "get_ents": ent, "get_exp": exp, "get_req": req})
    elif text:
        data = json.dumps({"text": text, "get_ents": ent, "get_exp": exp, "get_req": req})
    example = {
        "url": "https://job-openings.monster.ca/telecommunications-designer-victoria-bc-ca-primary-engineering-construction/221632928",
        "get_ents": True,
        "get_exp": True,
        "get_req": True}

    st.subheader("Example Query")
    st.json(example)
    test = st.checkbox("Would you like to use the test query as an example?")
    if test:
        data = json.dumps(example)
    # we only send it once the button is pressed to prevent preemptive erring
    if st.button("Press to send query"):
        response = requests.post(f"{base_url}/job-details", headers=headers, data=data, timeout=1000)
        st.json(response.json())


elif app_mode == "Show JD similarity":
    st.header("Show how similarity in job descriptions and resumes")
    st.subheader("""
                        This route is for describing the similarity between job descriptions and resumes.

                        The API will output a list of resumes and the result of how similar each one was to the given JD 

                        -   First supply your AWS credentials. This will be necessary for accessing your s3 bucket

                        -   Are you inputting data as a list of URLS or plaintext, use the checkboxes to specify your
                        input type
                        
                        -   Query the API when you are done!
                        """
                 )
    local_aws = st.radio("Are your files stored local or on AWS", ["Local", "AWS"])
    # todo mix local and AWS for resume
    if local_aws == 'AWS':
        access_key = st.text_input("What is your AWS Access Key")
        secret_key = st.text_input("What is your AWS Secret Key", type='password')
        is_url = st.checkbox('Is your data URLs or text? check box for URLs')
        resume_bucket = st.text_input('What is the name of your s3 bucket?')
        bucket_folder = st.text_input(
            'What is the name of the folder within your s3 bucket? (leave blank if in top level directory)')
        textbox = st.text_area("Input your job description text or urls as a list of strings i.e ['url1','url2']",
                               height=400)
        # getting a nice list from streamlit isnt convenient so we make the user type in a python list and then literally evaluate it.
        # There should be a cleaner solution and this should be changed if possible
        jds = literal_eval(textbox) if is_url else [textbox]
        headers = {'Content-Type': 'application/json', 'x-api-key': api_key}
        data = json.dumps(
            {"url_present": is_url, "resume_bucket": resume_bucket, "bucket_folder": bucket_folder, "jd": jds,
             "aws_key": access_key, "aws_secret_key": secret_key})
        if st.button("Press to send query"):
            response = requests.post(f"{base_url}/similarity", headers=headers, data=data)
            st.json(response.json())
    # send the request and print the results
    if local_aws == 'Local':
        headers = {'x-api-key': api_key}
        jds = st.file_uploader("Choose your job descriptions", accept_multiple_files=True)
        resumes = st.file_uploader("Choose your resumes", accept_multiple_files=True)
        files = []
        for i, jd in enumerate(jds):
            stream = io.BytesIO(jd.getvalue())
            files.append((f"jd_{jd.name}", stream))
        for i, resume in enumerate(resumes):
            stream = io.BytesIO(resume.getvalue())
            files.append((f"resume_{resume.name}", stream))
        if st.button("Press to send query"):
            response = requests.post(f'{base_url}/similarity', files=files, headers=headers)
            st.json(response.json())


elif app_mode == "Visualize NER training data":

    st.header("Visualize training data from the Named Entity model")
    st.subheader("""
                        This route is for collecting information about the data used to train NER models.

                        This page can lead to insights about what language 

                        -   paste in the URL to the job description you are searching for,
                         make sure the URL is to the Job page and not your search page!

                        -   Use the checkboxes to indicate what information you want to get 
                        from the API and then send it off!"""
                 )
    file = st.file_uploader("Upload an NER manifest file")

    if session_state.file_obj is None or (file is not None and session_state.file_obj != file):
        session_state.file_obj = file
    # Upload a training manifest file and visualize it
    use_ex = st.checkbox("Would you like to use an example file?")
    if use_ex:
        session_state.file_obj = open('NER-new.manifest', encoding='utf-8')

    if file is not None:
        session_state.reader = jsonlines.Reader(session_state.file_obj)
        lemma = WordNetLemmatizer()

        data = [obj for obj in session_state.reader]

        if (session_state.data is None and data) or (data and data != session_state.data):
            session_state.data = data

        data_list = []
        label_count = {}
        # create a list of words and their labels. Remove all punctuation and stopwords during this process
        session_state.data = [{remap(k): v for k, v in obj.items()} for obj in session_state.data]

        for jd in session_state.data:
            description = jd['source']
            for entity in jd['batch']['annotations']['entities']:  # todo make this different depending on group
                begin, end = entity['startOffset'], entity['endOffset']
                labeled_words = description[begin:end].translate(
                    str.maketrans(string.punctuation, ' ' * len(string.punctuation))).split(" ")
                labeled_words = [lemma.lemmatize(word) for word in labeled_words if
                                 word not in stopwords.words('english')]
                data_list.append((labeled_words, entity['label']))
                if entity['label'] in label_count:
                    label_count[entity['label']] += 1
                else:
                    label_count[entity['label']] = 0

        count = {}

        # use the prior data list to make a count of all the times a word is associated with a given lavel
        for item in data_list:
            for word in item[0]:
                if word.lower() in count and item[1] in count[word.lower()]:
                    count[word.lower()][item[1]] += 1
                else:
                    count[word.lower()] = {}
                    count[word.lower()][item[1]] = 1
        # create a dataframe from that count and display it to the user
        df = pd.DataFrame.from_dict(count)
        df = df.T
        df = df.fillna(0)
        st.dataframe(df)

        df = df.rename(rename, axis='columns')

        col_list = tuple(df.columns)

        if not session_state.col_list or (col_list and col_list != session_state.col_list):
            session_state.col_list = col_list

        # filter the dataframe based on which labels they want to see
        cols = st.multiselect("What labels would you like to view", session_state.col_list,
                              default=session_state.col_list)
        # filter the dataframe based on the number of occurrences of a word
        filter_num = st.slider("How many minimum occurrences do you need", 0, 100, value=15)
        df = df[cols]
        df['sums'] = df.sum(axis=1)

        df = df[df.sums > filter_num]
        df = df.drop(columns=['sums'])
        # create a bar chart with a bar for every word
        st.bar_chart(df)

        st.text("Total Labels")
        # display the total words labeled per soft skill

        for k, v in label_count.items():
            label_count[k] = {'count': v}
        labels_df = pd.DataFrame.from_dict(label_count)
        st.bar_chart(labels_df.T)
