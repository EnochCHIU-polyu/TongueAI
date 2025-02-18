import os
import toml
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from personal_info import show_personal_info
from tongue_detect import show_tongue_detect
from Weather import show_weather
from recommendation import show_recommendation
import streamlit as st


# Load API key from secrets manager
secrets = st.secrets

token = secrets['OPENAI']['OPENAI_API_KEY']
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

# Initialize session state for page with a welcom page not tonge detect
if 'page' not in st.session_state:
    st.session_state.page = "main"
# setup the main page and clear page first
def show_main():
    st.title("Welcome to the AI Assistant")
    st.write("This is a demo of an AI assistant that can help you with a variety of tasks.")
    st.write("Use the sidebar to navigate between different sections.")
    st.write("You can ask questions, get recommendations, and more!")


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

if page == "main":
    show_main()
elif page == "Personal Info":
    show_personal_info()
elif page == "Tongue Detect":
    show_tongue_detect(client, model_name)
elif page == "Weather Info":
    show_weather()
elif page == "Recommendation":
    show_recommendation()


