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

if 'language' not in st.session_state:
    st.session_state.language = 'ENG'
if 'camera' not in st.session_state:
    st.session_state.camera = False
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'uploaded_State' not in st.session_state:
    st.session_state.uploaded_State = False

def show_herb(client, model_name):
    st.title("Herb Check" if st.session_state.language == "ENG" else "藥材查詢")
    
    # Create a submit button for upload image by camera or file
    st.markdown("### Upload an image" if st.session_state.language == "ENG" else "### 上傳圖片")
    
    # Button to ask user to take a picture or not
    if st.button("Take a picture" if st.session_state.language == "ENG" else "拍照"):
        st.session_state.camera = True
    
    # Setup a close button to close the camera
    if st.button("Close camera" if st.session_state.language == "ENG" else "關閉相機"):
        st.session_state.camera = False
    
    def camera():
        if st.session_state.camera:
            uploaded_file = st.camera_input("Take a picture" if st.session_state.language == "ENG" else "拍照")
            if uploaded_file is not None:
                st.session_state.uploaded_file = uploaded_file
                # add a bttuon to submit the image
                if st.button("Submit" if st.session_state.language == "ENG" else "提交"):
                    st.session_state.uploaded_State = True


    # Call the camera function
    camera()
    
    with st.form(key="tongue_detect_form"):
        uploaded_file = st.file_uploader("Upload an image" if st.session_state.language == "ENG" else "上傳圖片", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.uploaded_State = True
        submit_button = st.form_submit_button(label="Submit" if st.session_state.language == "ENG" else "提交")

   
    if st.session_state.uploaded_State:
        if uploaded_file is not None:
            st.session_state['uploaded_file'] = uploaded_file
        
        # Enhance the prompt for better herb searching in traditional Chinese medicine
        if st.session_state.language == "ENG":
            user_prompt = "Analyze the uploaded image for provide detailed information about these herbs, including their names, properties, uses, and any precautions."

            system_prompt = (
            "You are an expert in traditional Chinese medicine. "
            "Provide detailed information about these herbs, including their names, properties, uses, and any precautions."
            )
        else:
            user_prompt = "分析上傳的圖片，根據中醫提供這些藥材的詳細信息，包括它們的名稱、性質、用途和任何注意事項。"

            system_prompt = (
            "您是一位中醫專家。"
            "提供這些藥材的詳細信息，包括它們的名稱、性質、用途和任何注意事項。"
            )

        if 'uploaded_file' in st.session_state:
            uploaded_file = st.session_state['uploaded_file']
            # Save the uploaded image to a temporary file
            temp_image_path = "herb_temp_image.png"
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
        st.markdown("## Response" if st.session_state.language == "ENG" else "## 回應")
        st.write(result)
    else:
        st.markdown("## Response" if st.session_state.language == "ENG" else "## 回應")
        st.write("Response: No result yet. Please submit your image." if st.session_state.language == "ENG" else "回應：尚無結果。請提交您的圖片。")