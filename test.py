import os
import toml

import streamlit as st


# Load API key from secrets manager
secrets = st.secrets

token = secrets['OPENAI']['OPENAI_API_KEY']

print(token)

import requests

def check_openai_api_key(token):
    url = "https://models.inference.ai.azure.com"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("OpenAI API key is valid.")
    else:
        print(f"OpenAI API key is invalid. Status code: {response.status_code}, Response: {response.text}")

# Replace 'your_openai_api_key' with your actual OpenAI API key
check_openai_api_key("token")