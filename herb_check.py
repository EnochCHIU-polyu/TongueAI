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
import os
import time
import base64

def show_herb(client, model_name):
    # Initialize all required session states if not already present
    if 'herb_analysis_result' not in st.session_state:
        st.session_state.herb_analysis_result = None
    if 'herb_analysis_loading' not in st.session_state:
        st.session_state.herb_analysis_loading = False
    if 'language' not in st.session_state:
        st.session_state.language = "ENG"
    if 'camera' not in st.session_state:
        st.session_state.camera = False
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'uploaded_State' not in st.session_state:
        st.session_state.uploaded_State = False
        
    lang = st.session_state.language
    
    # Page header
    st.markdown(f"<h1 style='color: #5D5CDE;'>{'Herb Checker' if lang == 'ENG' else '藥材查詢'}</h1>", unsafe_allow_html=True)
    
    # Main layout using columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Introduction
        intro_title = "📋 About Herb Identification" if lang == "ENG" else "📋 關於藥材識別"
        intro_text1 = ("Herb identification is essential in Traditional Chinese Medicine (TCM). "
                      "Proper identification ensures the correct herbs are used for treatment and helps avoid harmful substitutes."
                      if lang == "ENG" else 
                      "藥材識別在中醫中至關重要。正確識別確保用於治療的藥材正確無誤，有助於避免有害的替代品。")
        intro_text2 = ("Upload or capture a clear image of herbs to receive detailed information about their properties and uses."
                      if lang == "ENG" else
                      "上傳或拍攝清晰的藥材圖片，以獲取關於其性質和用途的詳細資訊。")
        
        st.markdown(f"""
        <div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h3 style="color: #333; margin-bottom: 15px;">{intro_title}</h3>
            <p style="color: #666; margin-bottom: 15px;">{intro_text1}</p>
            <p style="color: #666;">{intro_text2}</p>
        </div>
        """, unsafe_allow_html=True)

        # Image Upload Section
        st.markdown(f"""
        <div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h3 style="color: #333; margin-bottom: 15px;">{'📷 Upload Herb Image' if lang == 'ENG' else '📷 上傳藥材圖片'}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for different upload methods
        tab1, tab2 = st.tabs(["📁 " + ("Upload Image" if lang == "ENG" else "上傳圖片"), 
                              "📸 " + ("Take Photo" if lang == "ENG" else "拍照")])
        
        with tab1:
            uploaded_file = st.file_uploader(
                "Choose an image file" if lang == "ENG" else "選擇圖片檔案", 
                type=["jpg", "jpeg", "png"],
                help="Upload a clear image of herbs for analysis" if lang == "ENG" else "上傳藥材的清晰圖片進行分析"
            )
            
            if uploaded_file is not None:
                try:
                    # Display the uploaded image
                    image = Image.open(uploaded_file)
                    st.image(image, use_column_width=True, caption="Uploaded Image" if lang == "ENG" else "上傳的圖片")
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
                    "Take a photo of herbs" if lang == "ENG" else "拍攝藥材照片",
                    help="Position the herbs clearly in the frame" if lang == "ENG" else "請將藥材清晰地放在框架中"
                )
                
                if camera_image is not None:
                    try:
                        # Display the captured image
                        image = Image.open(camera_image)
                        st.session_state.uploaded_file = camera_image
                        st.session_state.uploaded_State = True
                    except Exception as e:
                        st.error(f"Error processing captured image: {e}")
                        st.session_state.uploaded_file = None
                        st.session_state.uploaded_State = False
        
        # Analysis button with enhanced styling
        if st.session_state.uploaded_State and not st.session_state.herb_analysis_loading:
            analyze_col1, analyze_col2 = st.columns([3, 1])
            with analyze_col1:
                if st.button(
                    "🔍 " + ("Analyze Herbs" if lang == "ENG" else "分析藥材"), 
                    type="primary",
                    use_container_width=True
                ):
                    st.session_state.herb_analysis_loading = True
                    st.session_state.herb_analysis_result = None
                    st.rerun()
            
            with analyze_col2:
                if st.button(
                    "🗑️ " + ("Clear" if lang == "ENG" else "清除"), 
                    type="secondary",
                    use_container_width=True
                ):
                    st.session_state.uploaded_file = None
                    st.session_state.uploaded_State = False
                    st.session_state.herb_analysis_result = None
                    st.session_state.herb_analysis_loading = False
                    st.rerun()
        
        # Image Guidelines
        with st.expander("📝 " + ("Image Guidelines" if lang == "ENG" else "圖片指南")):
            st.markdown("""
            #### Tips for good herb images:
            
            - Take the photo in natural daylight if possible
            - Include the entire herb in the frame
            - If possible, include both the whole herb and a cross-section
            - Place herbs against a neutral background
            - Make sure the image is in focus and properly exposed
            - Include multiple angles if the herb has distinctive features
            """ if lang == "ENG" else """
            #### 獲取良好藥材圖片的提示：
            
            - 如果可能，在自然日光下拍攝照片
            - 將整個藥材包含在畫面中
            - 如果可能，包括整個藥材和橫截面
            - 將藥材放在中性背景上
            - 確保圖像對焦清晰並曝光適當
            - 如果藥材有獨特特徵，請包括多個角度
            """)
    
    # Process the analysis on the right column
    with col2:
        # Result container
        st.markdown(f"""
        <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h3 style="color: #333; margin-bottom: 15px;">{'📊 Analysis Results' if lang == 'ENG' else '📊 分析結果'}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Loading state or results
        if st.session_state.herb_analysis_loading:
            with st.spinner("Analyzing herb image... Please wait" if lang == "ENG" else "分析藥材圖片中...請稍候"):
                # Process the image with Azure AI
                if 'uploaded_file' in st.session_state and st.session_state.uploaded_file is not None:
                    try:
                        uploaded_file = st.session_state.uploaded_file
                        
                        # Save the uploaded image to a temporary file
                        temp_image_path = "herb_temp_image.png"
                        with open(temp_image_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Set up prompts based on language
                        if lang == "ENG":
                            user_prompt = "Analyze the uploaded image and provide detailed information about these herbs, including their names, properties, uses, and any precautions."
                            system_prompt = (
                                "You are an expert in traditional Chinese medicine. "
                                "Provide detailed information about these herbs, including their names, properties, uses, and any precautions. "
                                "Structure your response in the following format:\n\n"
                                "## Herb Identification\n"
                                "[Name of the herb(s) identified in the image]\n\n"
                                "## Properties\n"
                                "- **Nature**: [e.g., warm, cold, neutral]\n"
                                "- **Taste**: [e.g., bitter, sweet, pungent]\n"
                                "- **Meridians**: [which meridians the herb enters]\n\n"
                                "## Traditional Uses\n"
                                "[Detailed description of how this herb is used in TCM]\n\n"
                                "## Modern Research\n"
                                "[Brief summary of any significant scientific findings]\n\n"
                                "## Precautions\n"
                                "[Any contraindications or side effects to be aware of]"
                            )
                        else:
                            user_prompt = "分析上傳的圖片，根據中醫提供這些藥材的詳細信息，包括它們的名稱、性質、用途和任何注意事項。"
                            system_prompt = (
                                "您是一位中醫專家。"
                                "提供這些藥材的詳細信息，包括它們的名稱、性質、用途和任何注意事項。"
                                "請按照以下格式提供回答：\n\n"
                                "## 藥材識別\n"
                                "[圖片中識別出的藥材名稱]\n\n"
                                "## 性質\n"
                                "- **性**: [例如，溫、寒、平]\n"
                                "- **味**: [例如，苦、甘、辛]\n"
                                "- **歸經**: [藥材歸屬的經絡]\n\n"
                                "## 傳統用途\n"
                                "[該藥材在中醫中如何使用的詳細描述]\n\n"
                                "## 現代研究\n"
                                "[任何重要科學發現的簡要總結]\n\n"
                                "## 注意事項\n"
                                "[任何需要注意的禁忌症或副作用]"
                            )
                        
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
                            
                            # Save results to session state
                            st.session_state.herb_analysis_result = result
                            
                            # Remove the temporary file
                            if os.path.exists(temp_image_path):
                                os.remove(temp_image_path)
                                
                        except Exception as e:
                            st.error(f"Error analyzing image: {str(e)}")
                            st.session_state.herb_analysis_result = f"Error: {str(e)}"
                    except Exception as e:
                        st.error(f"Error processing image: {str(e)}")
                        st.session_state.herb_analysis_result = f"Error: {str(e)}"
                
                # Turn off loading state
                st.session_state.herb_analysis_loading = False
                st.rerun()
        
        # Display results if available (outside the loading condition)
        if st.session_state.herb_analysis_result:
            result = st.session_state.herb_analysis_result
            
            # Display the full analysis
            with st.container(border=True):
                st.markdown(result)
            
            # Add a save or share button
            if st.button("💾 " + ("Save Analysis" if lang == "ENG" else "保存分析"), use_container_width=True):
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"herb_analysis_{timestamp}.txt"
                
                # Create a download link for the analysis
                def get_download_link(text, filename):
                    b64 = base64.b64encode(text.encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Click here to download</a>'
                    return href
                
                download_link = get_download_link(result, filename)
                st.markdown(f"{'Your analysis is ready for download:' if lang == 'ENG' else '您的分析已準備好下載：'} {download_link}", unsafe_allow_html=True)
            
            # New analysis button
            if st.button(
                "🔄 " + ("Analyze Another Herb" if lang == "ENG" else "分析另一個藥材"),
                type="primary",
                use_container_width=True,
                key="analyze_new_herb"
            ):
                st.session_state.uploaded_file = None
                st.session_state.uploaded_State = False
                st.session_state.herb_analysis_result = None
                st.session_state.herb_analysis_loading = False
                st.rerun()
        else:
            # Show placeholder when no results
            st.info("Upload and analyze an herb image to see results here" if lang == "ENG" else "上傳並分析藥材圖片以在此處查看結果")
    
    # Information about herbs (at the bottom of the page)
    with st.expander("ℹ️ " + ("About Chinese Herbs in TCM" if lang == "ENG" else "關於中藥材")):
        st.markdown("""
        ## The Role of Herbs in Traditional Chinese Medicine
        
        Chinese herbs form the foundation of TCM's medicinal approach. Key aspects include:
        
        - **Classification**: Herbs are categorized by properties (hot, warm, cool, cold) and flavors (sweet, sour, bitter, pungent, salty)
        - **Formulations**: Herbs are typically combined in precise formulas rather than used individually
        - **Processing Methods**: Raw herbs may be processed different ways to enhance certain properties or reduce side effects
        - **Quality Identification**: The quality, region of origin, and harvest time all affect an herb's therapeutic value
        
        Herbs are always prescribed as part of a holistic treatment approach that considers the individual's unique condition, constitution, and environmental factors.
        """ if lang == "ENG" else """
        ## 藥材在傳統中醫中的角色
        
        中藥材是中醫藥療法的基礎。主要方面包括：
        
        - **分類**：藥材按性質（熱、溫、涼、寒）和味道（甘、酸、苦、辛、鹹）分類
        - **配方**：藥材通常以精確的配方組合使用，而不是單獨使用
        - **加工方法**：原藥材可能會經過不同的加工方式，以增強某些特性或減少副作用
        - **質量識別**：藥材的質量、產地和採收時間都會影響其療效
        
        藥材總是作為整體治療方法的一部分處方，該方法考慮個體的獨特狀況、體質和環境因素。
        """)
    
    # Add dark mode support via custom CSS
    st.markdown("""
    <style>
        /* Dark mode overrides */
        @media (prefers-color-scheme: dark) {
            div[data-testid="stVerticalBlock"] > div:nth-child(1) {
                background-color: #262730;
            }
            
            div[style*="background-color: white"] {
                background-color: #2d2d2d !important;
                border-color: #444 !important;
            }
            
            h3[style*="color: #333"], h4 {
                color: #e0e0e0 !important;
                border-bottom-color: #444 !important;
            }
            
            p, div {
                color: #e0e0e0 !important;
            }
            
            div[style*="background-color: #f1f1f1"] {
                background-color: #444 !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)