## Job Description Algorithm

This repo is an API designed to extract information relevant to Nugget's hiring process right from a URL to a job
description. It is set up as a flask API and has a streamlit web app frontend for interacting with a GUI instead
of a RESTful API. All the files relevant to the API are contained within src.

---

### Installation

- Install dependencies run `pip install -r requirements.txt`

### Running the code from docker

- docker-compose up -d

Option d: That option is called detached mode, meaning the commands will run in the background and you won't see the information they are sending

### Running the code locally

- All scripts in the `scripts` folder are one off files used to create the data and code necessary for this project.
  They can all be run individually
- The code in the `src` folder is the API. It consists of the Flask API and a streamlit GUI. To run them both locally run the app.py file as the main file then in a new terminal run `streamlit run demo_app.py` This will start
  running the API as well as locally open up the streamlit GUI.

## Using the API

There are currently 3 routes which make up the API. The first is the general query - job scrape endpoint. It ends in a generic '/'. The parameters that need to be passed to this endpoint are

1. a URL

Input to the API route is in this format

```
{"url":"<url>""}
```

The output from this route will

The second route is the document similarity route. This one takes 6 pieces of input

1. resume_bucket
2. jd
3. url_present
4. bucket_folder
5. AWS Access Key
6. AWS Secret Access Key

The resume bucket is a bucket where the resumes are stored in s3. Bucket folder is a subfolder in the s3 bucket.
url_present determines if the JDs are accessed through a url or plaintext.
Jd is dynamic and either a list of urls or strings depending on the value of is_url.
The AWS credentials are what the API uses to log in to your AWS account to access your bucket.
It is recommended you create a role and generate access keys for the API

Input is as follows

```
{
    "resume_bucket": "<bucket>",
    "bucket_folder": "<folder>",
    "url_present": <boolean>,
    "jd_url": [
        "<list item>",
        "<list item>",
        "<list item>"
    ],
    "aws_key":'<key>',
    "aws_secret_key":'<aws_secret_key>'
}
```

The third route connects to the named entity model. The route connects to a custom NER model designed to label text adn what soft skills are associated with it.
The model takes 2 parameters

1. text
2. is_url

The text field is either a URL or the raw text of a job description. The model will then return a dictionary containing information about where the soft skills are in the text as well as their relative importance.

Input is as follows

```
{
    "text":<text>,
    "is_url":<boolean>
}
```

- Running `pytest` from the root directory will run the test suite. More granular instructions can be found using pytest's
  documentation.

### General tips

- All code and scripts have docstrings and comments. Most usage instructions can be found within the files themselves, this is especially true of the scripts folder.
