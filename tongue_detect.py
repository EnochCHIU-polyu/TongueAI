import streamlit as st
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage,
    UserMessage,
    TextContentItem,
    ImageContentItem,
    ImageUrl,
    ImageDetailLevel,
)
from azure.core.credentials import AzureKeyCredential
from PIL import Image
import io

def show_tongue_detect(client, model_name):
    st.title("Tongue Detect")
    st.markdown("### Upload an image and ask a question")

    with st.form(key="tongue_detect_form"):
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if 'uploaded_file' in st.session_state:
            uploaded_file = st.session_state['uploaded_file']

        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if uploaded_file is not None:
            st.session_state['uploaded_file'] = uploaded_file
        user_prompt = "Can you help me with a traditional chinese medical diagnosis by tongue detection?"
        system_prompt = "Answer questions in traditional chinese, refer to the image for more context, and act like a traditional chinese medical expert. For detail please having the info in 5 type 1. 舌體顏色, 2. 舌質, 3. 舌苔, 4. 舌形, 5. 舌下血管, and finally giving a mark from 1-100. And give a diagnosis  with at least 3 type Chinese medicine prescription based on the information."
        
        if 'uploaded_file' in st.session_state:
            uploaded_file = st.session_state['uploaded_file']
            # Save the uploaded image to a temporary file
            temp_image_path = "temp_image.png"
            with open(temp_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Call the Azure AI model with the image URL
            response = client.complete(
                messages=[
                    SystemMessage(content=system_prompt),
                    UserMessage(
                        content=[
                            TextContentItem(text=user_prompt),
                            ImageContentItem(
                                image_url=ImageUrl.load(
                                    image_file=temp_image_path,
                                    image_format="jpg",
                                    detail=ImageDetailLevel.LOW)
                            ),
                        ],
                    ),
                ],
                model=model_name,
            )
            
            result = response.choices[0].message.content
            st.session_state['result'] = result
        else:
            result = "Please upload an image."
            st.session_state['result'] = result
        
    if 'result' in st.session_state:
        st.markdown("## Response")
        st.write("Response: Please see the result on Recommendation page.")
    else:
        st.markdown("## Response")
        st.write("Response: No result yet. Please submit your image.")