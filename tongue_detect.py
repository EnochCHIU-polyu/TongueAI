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

def show_tongue_detect(client, model_name):
    st.title("Tongue Detect" if st.session_state.language == "ENG" else "舌診")
    
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
        if st.session_state.language == "ENG":
            user_prompt = "Please help me make a tongue diagnosis."
            system_prompt = "Answer the questions in Engish, refer to the image for more background information, and act like a TCM expert. Provide 4 types of information: 1. Tongue body color, 2. Tongue quality, 3. Tongue coating, 4. Tongue shape, and give a score of 1-100 based on these information. Provide at least 3 types of Chinese medicine prescriptions based on these information"
        else:
            user_prompt = "請幫我做一個舌診的中醫診斷。"
            system_prompt = "回答問題時請使用中文，參考圖片以獲得更多背景資料，並表現得像一位中醫專家。詳細請提供4種類型的信息根據圖片舌頭的資料：1. 舌體顏色, 2. 舌質, 3. 舌苔, 4. 舌形，最後給出一個1-100的分數。並根據這些信息給出診斷，至少提供3種中藥處方。"

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
        st.markdown("## Response" if st.session_state.language == "ENG" else "## 回應")
        st.write("Response: Please see the result on Recommendation page." if st.session_state.language == "ENG" else "回應：請查看推薦頁面上的結果。")
    else:
        st.markdown("## Response" if st.session_state.language == "ENG" else "## 回應")
        st.write("Response: No result yet. Please submit your image." if st.session_state.language == "ENG" else "回應：尚無結果。請提交您的圖片。")