import os
import toml
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import streamlit as st


# Load API key from secrets manager

secrets = st.secrets

def answer(system_prompt, user_prompt, image=None, model_type="openrouter"):
    if model_type == "openrouter":
        print("Answer using Openrouter API")
        endpoint = "https://openrouter.ai/api/v1"
        if 'OPENROUTER' not in secrets or 'OPENROUTER_API_KEY' not in secrets['OPENROUTER']:
            # throw an error if the API key is not found
            raise ValueError("OpenRouter API key not found")
        else:
            token = secrets['OPENROUTER']['OPENROUTER_API_KEY']
    elif model_type == "openai":
        print("Answer using OpenAI API")
        endpoint = "https://models.inference.ai.azure.com"
        if 'OPENAI' not in secrets or 'OPENAI_API_KEY' not in secrets['OPENAI']:
            # throw an error if the API key is not found
            raise ValueError("OpenAI API key not found")
        else:
            token = secrets['OPENAI']['OPENAI_API_KEY']
    else:
        raise ValueError("Invalid API type")

    model_name = "gpt-4o-mini"

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )

    messages = [
        SystemMessage(content=system_prompt),
        UserMessage(content=user_prompt),
    ]
    
    if image is not None:
        # Add image processing logic here if the model supports it
        # For example, you might need to convert the image to a specific format
        # and include it in the messages or as a separate parameter
        pass

    response = client.complete(
        messages=messages,
        max_tokens=1000,
        model=model_name
    )

    return response.choices[0].message.content
    
from openai import OpenAI


def advice_llm(system_prompt, user_prompt, model_type="openai"):
    if model_type == "openrouter":
        print("Answer using Openrouter API")
        endpoint = "https://openrouter.ai/api/v1"
        if 'OPENROUTER' not in secrets or 'OPENROUTER_API_KEY' not in secrets['OPENROUTER']:
            raise ValueError("OpenRouter API key not found")
        token = secrets['OPENROUTER']['OPENROUTER_API_KEY']
    elif model_type == "openai":
        print("Answer using OpenAI API")
        endpoint = "https://models.inference.ai.azure.com"
        if 'OPENAI' not in secrets or 'OPENAI_API_KEY' not in secrets['OPENAI']:
            raise ValueError("OpenAI API key not found")
        token = secrets['OPENAI']['OPENAI_API_KEY']
    else:
        raise ValueError(f"Invalid API type: {model_type}. Expected 'openai' or 'openrouter'.")

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token)
    )

    response = client.complete(
        messages=[
            SystemMessage(content=system_prompt),
            UserMessage(content=user_prompt)
        ],
        max_tokens=1000,
        model="gpt-4o-mini"
    )

    return response.choices[0].message.content

# execute if the script is run directly
if __name__ == "__main__":
    model_type = "openai"
    result = advice_llm("Answer in chinese", "What is the capital of France?", model_type)
    print(result)