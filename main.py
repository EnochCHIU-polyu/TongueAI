import os
import toml
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from personal_info import show_personal_info
from tongue_detect import show_tongue_detect
from Weather import show_weather
from recommendation import show_recommendation
from herb_check import show_herb
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

# Initialize session state for page with a welcome page not tongue detect
if 'page' not in st.session_state:
    st.session_state.page = "main"
# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = "ENG"
if 'language' not in st.session_state:
    st.session_state.language = 'ENG'
if 'camera' not in st.session_state:
    st.session_state.camera = False
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'uploaded_State' not in st.session_state:
    st.session_state.uploaded_State = False

# Function to show the main page
def show_main():
    if st.session_state.language == "ENG":
        st.title("Welcome to the AI Traditional Chinese Medicine Assistant")
        st.write("This AI-powered assistant provides personalized health advice and Traditional Chinese Medicine (TCM) prescriptions based on your health condition.")
        st.write("Use the sidebar to navigate through different features and explore TCM wisdom.")
        st.write("Enter your health concerns, and the AI will offer recommendations based on TCM principles!")
    else:
        st.title("歡迎使用AI中醫助手")
        st.write("這個AI助手根據您的健康狀況提供個性化的健康建議和中醫處方。")
        st.write("使用側邊欄導航不同功能，探索中醫智慧。")
        st.write("輸入您的健康問題，AI將根據中醫原則提供建議！")

# Sidebar for navigation and language switcher with col 1/3
def show_sidebar():
    st.sidebar.title("Language/語言")
    col1, col2, col3, col4 = st.sidebar.columns([1, 1, 1, 1])
    with col1:
        if st.button("中文"):
            st.session_state.language = "中文"
    with col2:
        if st.button("ENG"):
            st.session_state.language = "ENG"

    st.sidebar.title("Navigation" if st.session_state.language == "ENG" else "導航")
    if st.sidebar.button("Go to Personal Info" if st.session_state.language == "ENG" else "個人信息"):
        st.session_state.page = "Personal Info"
    if st.sidebar.button("Go to Tongue Detect" if st.session_state.language == "ENG" else "舌診"):
        st.session_state.page = "Tongue Detect"
    if st.sidebar.button("Go to Weather Info" if st.session_state.language == "ENG" else "天氣信息"):
        st.session_state.page = "Weather Info"
    if st.sidebar.button("Go to Recommendation" if st.session_state.language == "ENG" else "推薦"):
        st.session_state.page = "Recommendation"
    if st.sidebar.button("Go to Herb Check" if st.session_state.language == "ENG" else "藥材查詢"):
        st.session_state.page = "Herb Check"

show_sidebar()


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
elif page == "Herb Check":
    show_herb(client, model_name)
