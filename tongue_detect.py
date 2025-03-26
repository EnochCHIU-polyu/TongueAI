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
import re
import os
join = os.path.join
import time
import base64

def show_tongue_detect(client, model_name):
    for f in os.listdir("data/combined_output"):
        os.remove(join("data/combined_output", f))
    for f in os.listdir("data/test_mask"):
        os.remove(join("data/test_mask", f))
    for f in os.listdir("data/real_ai_input"):
        os.remove(join("data/real_ai_input", f))

    # Initialize all required session states if not already present
    if 'tongue_analysis_result' not in st.session_state:
        st.session_state.tongue_analysis_result = None
    if 'tongue_analysis_score' not in st.session_state:
        st.session_state.tongue_analysis_score = None
    if 'tongue_analysis_loading' not in st.session_state:
        st.session_state.tongue_analysis_loading = False
    if 'language' not in st.session_state:
        st.session_state.language = "ENG"
    if 'camera' not in st.session_state:
        st.session_state.camera = False
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'uploaded_State' not in st.session_state:
        st.session_state.uploaded_State = False
    if 'page' not in st.session_state:
        st.session_state.page = "Tongue Diagnosis"
    camera_image = None
    uploaded_file = None
    lang = st.session_state.language
    
    # Navigation - Add this at the top of the page
    nav_col1, nav_col2 = st.columns([6, 4])
    with nav_col1:
        st.markdown(f"<h1 style='color: #5D5CDE;'>{'Tongue Diagnosis' if lang == 'ENG' else '舌診分析'}</h1>", unsafe_allow_html=True)

    
    # Main layout using columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Introduction
        intro_title = "📋 About Tongue Diagnosis" if lang == "ENG" else "📋 關於舌診"
        intro_text1 = ("Tongue diagnosis is a crucial diagnostic method in Traditional Chinese Medicine (TCM). "
                      "The tongue's appearance reflects the body's internal health and can reveal imbalances in the organs and meridians."
                      if lang == "ENG" else 
                      "舌診是中醫診斷的重要方法。舌頭的外觀反映了身體的內部健康狀況，可以揭示臟腑和經絡的不平衡。")
        intro_text2 = ("Upload or capture a clear image of your tongue to receive a comprehensive TCM analysis."
                      if lang == "ENG" else
                      "上傳或拍攝一張清晰的舌頭圖片，以獲得全面的中醫分析。")
        
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h3 style=" margin-bottom: 15px;">{intro_title}</h3>
            <p style=" margin-bottom: 15px;">{intro_text1}</p>
            <p style="">{intro_text2}</p>
        </div>
        """, unsafe_allow_html=True)

        # Image Upload Section
        st.markdown(f"""
        <div style=" border-radius: 10px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h3 style=" margin-bottom: 15px;">{'📷 Upload Tongue Image' if lang == 'ENG' else '📷 上傳舌頭圖片'}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for different upload methods
        tab1, tab2 = st.tabs(["📁 " + ("Upload Image" if lang == "ENG" else "上傳圖片"), 
                              "📸 " + ("Take Photo" if lang == "ENG" else "拍照")])
        
        with tab1:
            uploaded_file = st.file_uploader(
                "Choose an image file" if lang == "ENG" else "選擇圖片檔案", 
                type=["jpg", "jpeg", "png"],
                help="Upload a clear image of your tongue for analysis" if lang == "ENG" else "上傳舌頭的清晰圖片進行分析"
            )
            
            if uploaded_file is not None:
                try:
                    # Display the uploaded image
                    image = Image.open(uploaded_file)
                    st.image(image, use_container_width=True, caption="Uploaded Image" if lang == "ENG" else "上傳的圖片")
                    st.session_state.uploaded_file = uploaded_file
                    st.session_state.uploaded_State = True
                except Exception as e:
                    st.error(f"Error opening image: {e}")
                    st.session_state.uploaded_file = None
                    st.session_state.uploaded_State = False
        
        with tab2:
            camera_placeholder = st.empty()
            with camera_placeholder.container():
                camera_image = st.camera_input(
                    "Take a photo of your tongue" if lang == "ENG" else "拍攝您的舌頭照片",
                    help="Position your tongue clearly in the frame" if lang == "ENG" else "請將舌頭清晰地放在框架中"
                )
                
                if camera_image is not None:
                    try:
                        # Display the captured image
                        image = Image.open(camera_image)
                        #st.image(image, use_container_width=True, caption="Captured Image" if lang == "ENG" else "拍攝的圖片")
                        st.session_state.uploaded_file = camera_image
                        st.session_state.uploaded_State = True
                    except Exception as e:
                        st.error(f"Error processing captured image: {e}")
                        st.session_state.uploaded_file = None
                        st.session_state.uploaded_State = False
        
        # Analysis button with enhanced styling
        if st.session_state.uploaded_State and not st.session_state.tongue_analysis_loading:
            analyze_col1, analyze_col2 = st.columns([3, 1])
            with analyze_col1:
                if st.button(
                    "🔍 " + ("Analyze Tongue" if lang == "ENG" else "分析舌頭"), 
                    type="primary",
                    use_container_width=True
                ):
                    st.session_state.tongue_analysis_loading = True
                    st.session_state.tongue_analysis_result = None
                    st.session_state.tongue_analysis_score = None
                    st.rerun()
            
            with analyze_col2:
                if st.button(
                    "🗑️ " + ("Clear" if lang == "ENG" else "清除"), 
                    type="secondary",
                    use_container_width=True
                ):
                    st.session_state.uploaded_file = None
                    st.session_state.uploaded_State = False
                    st.session_state.tongue_analysis_result = None
                    st.session_state.tongue_analysis_score = None
                    st.session_state.tongue_analysis_loading = False
                    st.rerun()
        
        # Image Guidelines
        with st.expander("📝 " + ("Image Guidelines" if lang == "ENG" else "圖片指南")):
            st.markdown("""
            #### Tips for a good tongue image:
            
            - Take the photo in natural daylight if possible
            - Extend your tongue fully but comfortably
            - Keep your mouth open wide enough to see the entire tongue
            - Avoid eating or drinking colored foods/beverages before the photo
            - Clean your tongue gently before taking the photo
            """ if lang == "ENG" else """
            #### 獲取良好舌頭圖片的提示：
            
            - 如果可能，在自然日光下拍攝照片
            - 完全但舒適地伸出舌頭
            - 保持嘴巴足夠張開，以便看到整個舌頭
            - 避免在拍照前食用或飲用有色食物/飲料
            - 拍照前輕輕清潔舌頭
            """)
    
    # Process the analysis on the right column
    with col2:
        # Result container
        st.markdown(f"""
        <div style=" border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h3 style=" margin-bottom: 15px;">{'📊 Diagnosis Results' if lang == 'ENG' else '📊 診斷結果'}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Loading state or results
        if st.session_state.tongue_analysis_loading:
            with st.spinner("Analyzing tongue image... Please wait" if lang == "ENG" else "分析舌頭圖片中...請稍候"):
                # Process the image with Azure AI
                if 'uploaded_file' in st.session_state and st.session_state.uploaded_file is not None:
                    try:
                        uploaded_file = st.session_state.uploaded_file
                        
                        # Save the uploaded image to a temporary file
                        temp_image_path = "temp_image.jpg"
                        with open(temp_image_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Set up prompts based on language
                        if lang == "ENG":
                            user_prompt = "Please help me make a tongue diagnosis."
                            system_prompt = """
                            Answer the questions in English, refer to the image for more background information, and act like a TCM expert. 
                            Structure your response in the following format:
                            
                            ## Tongue Analysis
                            
                            ### Tongue Body Color
                            [Detailed description of tongue body color]
                            
                            ### Tongue Quality
                            [Detailed description of tongue quality]
                            
                            ### Tongue Coating
                            [Detailed description of tongue coating]
                            
                            ### Tongue Shape
                            [Detailed description of tongue shape]
                            
                            ## Health Score
                            [A score from 1-100 based on the tongue analysis, with 100 being perfectly healthy]
                            
                            ## TCM Diagnosis
                            [Your diagnosis based on the tongue analysis]
                            
                            ## Recommended Herbal Prescriptions
                            1. [Prescription name] - [Brief description and benefits]
                            2. [Prescription name] - [Brief description and benefits]
                            3. [Prescription name] - [Brief description and benefits]
                            """
                        else:
                            user_prompt = "請幫我做一個舌診的中醫診斷。"
                            system_prompt = """
                            回答問題時請使用中文，參考圖片以獲得更多背景資料，並表現得像一位中醫專家。
                            請按照以下格式提供回答：
                            
                            ## 舌頭分析
                            
                            ### 舌體顏色
                            [舌體顏色的詳細描述]
                            
                            ### 舌質
                            [舌質的詳細描述]
                            
                            ### 舌苔
                            [舌苔的詳細描述]
                            
                            ### 舌形
                            [舌形的詳細描述]
                            
                            ## 健康評分
                            [根據舌頭分析的1-100分評分，100分為最健康]
                            
                            ## 中醫診斷
                            [根據舌頭分析的診斷]
                            
                            ## 推薦的中藥處方
                            1. [處方名稱] - [簡要描述和好處]
                            2. [處方名稱] - [簡要描述和好處]
                            3. [處方名稱] - [簡要描述和好處]
                            """
                        
                        # Call the Azure AI model with the image
                        try:
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
                            
                            # Extract score from the result using regex
                            score_pattern = r"## Health Score\s*(\d+)" if lang == "ENG" else r"## 健康評分\s*(\d+)"
                            score_match = re.search(score_pattern, result)
                            score = int(score_match.group(1)) if score_match else None
                            
                            # Save results to session state
                            st.session_state.tongue_analysis_result = result
                            st.session_state.tongue_analysis_score = score
                            
                            # Remove the temporary file
                            if os.path.exists(temp_image_path):
                                os.remove(temp_image_path)
                                
                        except Exception as e:
                            st.error(f"Error analyzing image: {str(e)}")
                            st.session_state.tongue_analysis_result = f"Error: {str(e)}"
                    except Exception as e:
                        st.error(f"Error processing image: {str(e)}")
                        st.session_state.tongue_analysis_result = f"Error: {str(e)}"
                
                # Turn off loading state
                st.session_state.tongue_analysis_loading = False
                st.rerun()
        
        # Display results if available (outside the loading condition)
        if st.session_state.tongue_analysis_result:
            result = st.session_state.tongue_analysis_result
            score = st.session_state.tongue_analysis_score
            
            # Create a health score gauge if score is available
            if score is not None:
                # Determine color based on score
                if score >= 80:
                    score_color = "#2ecc71"  # Green
                elif score >= 60:
                    score_color = "#f39c12"  # Orange
                else:
                    score_color = "#e74c3c"  # Red
                
                # Display score gauge
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 25px;">
                    <h4 style="margin-bottom: 10px;">{'Health Score' if lang == 'ENG' else '健康評分'}</h4>
                    <div style="font-size: 48px; font-weight: bold; color: {score_color};">{score}</div>
                    <div style="width: 100%; height: 20px; background-color: #f1f1f1; border-radius: 10px; margin: 10px 0;">
                        <div style="width: {score}%; height: 100%; border-radius: 10px; background-color: {score_color};"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #777;">
                        <span>0</span>
                        <span>50</span>
                        <span>100</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Display the full analysis
            st.markdown(result)
            
            # Add a save or share button
            if st.button("💾 " + ("Save Analysis" if lang == "ENG" else "保存分析"), use_container_width=True):
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"tongue_analysis_{timestamp}.txt"
                
                # Create a download link for the analysis
                def get_download_link(text, filename):
                    b64 = base64.b64encode(text.encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Click here to download</a>'
                    return href
                
                download_link = get_download_link(result, filename)
                st.markdown(f"{'Your analysis is ready for download:' if lang == 'ENG' else '您的分析已準備好下載：'} {download_link}", unsafe_allow_html=True)
        else:
            # Show placeholder when no results
            st.info("Upload and analyze a tongue image to see results here" if lang == "ENG" else "上傳並分析舌頭圖片以在此處查看結果")
    
    # Information about tongue diagnosis (at the bottom of the page)
    with st.expander("ℹ️ " + ("About Tongue Diagnosis in TCM" if lang == "ENG" else "關於中醫舌診")):
        st.markdown("""
        ## The Importance of Tongue Diagnosis
        
        In Traditional Chinese Medicine (TCM), the tongue is considered a window to the body's internal health. Practitioners assess:
        
        - **Tongue Body Color**: Reflects the state of blood, qi, and yin-yang balance
        - **Tongue Coating**: Indicates conditions in the digestive system and presence of pathogens
        - **Tongue Shape**: Shows excess or deficiency patterns
        - **Moisture**: Reveals body fluid status
        
        Tongue diagnosis is always used alongside other diagnostic methods such as pulse diagnosis, patient history, and physical examination for a comprehensive assessment.
        """ if lang == "ENG" else """
        ## 舌診的重要性
        
        在中醫中，舌頭被視為身體內部健康的窗口。醫師評估：
        
        - **舌體顏色**：反映血液、氣和陰陽平衡的狀態
        - **舌苔**：指示消化系統的狀況和病原體的存在
        - **舌形**：顯示過剩或不足的模式
        - **濕度**：揭示體液狀態
        
        舌診始終與其他診斷方法一起使用，如脈診、病史和體格檢查，以進行全面評估。
        """)


# The main script would typically have a structure like this:
# if __name__ == "__main__":
#     # Connect to Azure AI client
#     client = ChatCompletionsClient(
#         endpoint="YOUR_ENDPOINT",
#         credential=AzureKeyCredential("YOUR_API_KEY")
#     )
#     model_name = "YOUR_MODEL_NAME"
#
#     # Check which page to display
#     if 'page' not in st.session_state:
#         st.session_state.page = "Tongue Diagnosis"
#     
#     page = st.session_state.page
#     
#     if page == "Tongue Diagnosis":
#         show_tongue_detect(client, model_name)
#     elif page == "Herb Check":
#         show_herb(client, model_name)