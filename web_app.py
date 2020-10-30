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
from spacy_streamlit import load_model

nltk.download('stopwords')
attrs = ["text", "label_", "start", "end", "start_char", "end_char"]

# here we are using streamlit to enable a webapp for the API
st.title("JD Algorithm")
st.set_option('deprecation.showfileUploaderEncoding', False)
# This lets us select different screens in streamlits sidebar
app_mode = st.sidebar.selectbox("Choose the app mode",
                                ["Collect JD details", "Show named entities", "Show JD similarity",
                                 "Visualize NER training data", "Get years of experience"])

if app_mode == "Collect JD details":
    # we grab a url from the user and send it by http request to the endpoint we want
    url = str(st.text_area("url"))
    is_text = st.checkbox("Is your input plaintext?")
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"url": url, "is_text": is_text})
    # we only send it once the button is pressed to prevent preemptive erring
    if st.button("Press to send query"):
        response = requests.get("http://13.58.185.40:6000/", headers=headers, data=data)
        st.json(response.json())


elif app_mode == "Show JD similarity":
    access_key = st.sidebar.text_input("What is your AWS Access Key")
    secret_key = st.sidebar.text_input("What is your AWS Secret Key", type='password')
    is_url = st.checkbox('Is your data URLs or text? check box for URLs')
    resume_bucket = st.text_input('What is the name of your s3 bucket?')
    bucket_folder = st.text_input(
        'What is the name of the folder within your s3 bucket? (leave blank if in top level directory)')
    textbox = st.text_area("Input your job description text or urls as a list of strings i.e ['url1','url2']",
                           height=400)
    # getting a nice list from streamlit isnt convenient so we make the user type in a python list and then literally evaluate it.
    # There should be a cleaner solution and this should be changed if possible
    jds = literal_eval(textbox) if is_url else [textbox]
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(
        {"url_present": is_url, "resume_bucket": resume_bucket, "bucket_folder": bucket_folder, "jd": jds,
         "aws_key": access_key, "aws_secret_key": secret_key})
    # send the request and print the results
    if st.button("Press to send query"):
        response = requests.get("http://13.58.185.40:6000/similarity", headers=headers, data=data)
        st.json(response.json())


elif app_mode == "Show named entities":
    text = st.text_area("Input the JD as plaintext or as a URL")
    is_url = st.checkbox('Is your input a URL?')
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"text": text, "is_url": is_url})
    if st.button('Press to send query'):
        response = requests.get("http://13.58.185.40:6000/NER", headers=headers, data=data)
        st.json(response.json())

elif app_mode == "Get years of experience":
    text = st.text_area("Input a resume or JD as text", height=500)
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"text": text})
    if st.button('Press to send query'):
        response = requests.get("http://13.58.185.40:6000/experience", headers=headers, data=data)
        st.json(response.json())

elif app_mode == "Visualize NER training data":
    file = st.file_uploader("Upload an NER manifest file")
    # Upload a training manifest file and visualize it
    if file is not None:
        reader = jsonlines.Reader(file)
        lemma = WordNetLemmatizer()

        data = [obj for obj in reader]

        data_list = []
        label_count = {}
        remap = {"source": "source", "jd-group-1": "jd", "jd-group-2": "jd",
                 "jd-group-1-metadata": "jd-group-1-metadata", "jd-group-2-metadata": "jd-group-2-metadata"}
        # create a list of words and their labels. Remove all punctuation and stopwords during this process
        data = [{remap[k]: v for k, v in obj.items()} for obj in data]
        for jd in data:
            description = jd['source']
            for entity in jd['jd']['annotations']['entities']:  # todo make this different depending on group
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
        # create a datafrome from that count and display it to the user
        df = pd.DataFrame.from_dict(count)
        df = df.T
        df = df.fillna(0)
        st.dataframe(df)
        # filter the dataframe based on which labels they want to see
        cols = st.multiselect("What labels would you like to view",
                              ("teamwork", "problem solving ", "interpersonal sensitivity", "organization",
                               "communication",
                               "leadership", "project management"),
                              default=("teamwork", "problem solving ", "interpersonal sensitivity", "organization",
                                       "communication",
                                       "leadership", "project management"))
        # filter the datafrome based on the number of occurrences of a word
        filter_num = st.slider("How many minimum occurrences do you need", 0, 100, value=15)
        df = df[cols]
        df['sums'] = df.sum(axis=1)

        df = df[df.sums > filter_num]
        df.drop(columns=['sums'], inplace=True)
        # create a bar chart with a bar for every word
        st.bar_chart(df)

        st.text("Total Labels")
        # display the total words labeled per soft skill
        for k, v in label_count.items():
            label_count[k] = {'count': v}
        labels_df = pd.DataFrame.from_dict(label_count)
        st.bar_chart(labels_df.T)
