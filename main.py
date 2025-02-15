import os
import toml
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from personal_info import show_personal_info
from tongue_detect import show_tongue_detect
from Weather import show_weather
from recommendation import show_recommendation
import streamlit as st


# Load API key from credentials.txt or secrets manager
file_path = 'credentials'
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        secrets = toml.load(f)
else:
    secrets = st.secrets

token = secrets['OPENAI']['OPENAI_API_KEY']
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

# Initialize session state for page
if 'page' not in st.session_state:
    st.session_state.page = "Tongue Detect"

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Go to Personal Info"):
    st.session_state.page = "Personal Info"
if st.sidebar.button("Go to Tongue Detect"):
    st.session_state.page = "Tongue Detect"
if st.sidebar.button("Go to Weather Info"):
    st.session_state.page = "Weather Info"
if st.sidebar.button("Go to Recommendation"):
    st.session_state.page = "Recommendation"

# Determine the current page
page = st.session_state.page

if page == "Personal Info":
    show_personal_info()
elif page == "Tongue Detect":
    show_tongue_detect(client, model_name)
elif page == "Weather Info":
    show_weather()
elif page == "Recommendation":
    show_recommendation()


