import streamlit as st
import requests
import json
import markdown
import re
from llm_openai import advice_llm
import time
import base64

def format_markdown_to_html(text):
    """Convert markdown to HTML with some additional styling"""
    if not text:
        return ""
    
    # Convert markdown to HTML
    html = markdown.markdown(text)
    
    # Add custom styling
    html = html.replace('<h1>', '<h1 style="color: #5D5CDE; font-size: 1.8rem; margin-top: 1.5rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #eee;">')
    html = html.replace('<h2>', '<h2 style="color: #5D5CDE; font-size: 1.5rem; margin-top: 1.2rem; margin-bottom: 0.8rem; padding-bottom: 0.4rem; border-bottom: 1px solid #eee;">')
    html = html.replace('<h3>', '<h3 style="color: #5D5CDE; font-size: 1.2rem; margin-top: 1rem; margin-bottom: 0.7rem;">')
    html = html.replace('<p>', '<p style="margin-bottom: 1rem; line-height: 1.6;">')
    html = html.replace('<ul>', '<ul style="margin-bottom: 1rem; padding-left: 1.5rem;">')
    html = html.replace('<li>', '<li style="margin-bottom: 0.5rem;">')
    
    return html

def extract_prescriptions(text):
    """Extract prescription sections from the recommendation text"""
    # Look for numbered prescriptions (1., 2., 3., etc) or bullet points
    # This regex is more flexible to handle different formats
    pattern = r'((?:\d+\.\s*|\*\s*|•\s*)([^\n]+(?:\n(?!\d+\.\s*|\*\s*|•\s*)[^\n]+)*))'
    
    matches = re.findall(pattern, text)
    prescriptions = []
    
    for match in matches:
        # Each match is a tuple with the full match and the captured group
        full_match = match[0]
        # Clean up the prescription text and add to the list
        clean_text = full_match.strip()
        if clean_text and len(clean_text) > 5:  # Avoid very short matches
            prescriptions.append(clean_text)
    
    # If no matches found with the pattern, try splitting by double newlines
    if not prescriptions:
        parts = text.split("\n\n")
        prescriptions = [part.strip() for part in parts if len(part.strip()) > 10]
    
    return prescriptions[:3]  # Return up to 3 prescriptions

def llm_recommendation():
    """Generate personalized TCM recommendations based on all available data"""
    # Initialize recommendation if not present
    if 'recommendation' not in st.session_state:
        st.session_state['recommendation'] = None
    if 'recommendation_loading' not in st.session_state:
        st.session_state['recommendation_loading'] = False
    if 'recommendation_time' not in st.session_state:
        st.session_state['recommendation_time'] = None
    if 'recommendation_language' not in st.session_state:
        st.session_state['recommendation_language'] = None
    
    lang = st.session_state.language
    language_changed = st.session_state.recommendation_language != lang and st.session_state.recommendation is not None

    # Check if we need to generate a new recommendation
    force_refresh = 'force_recommendation_refresh' in st.session_state and st.session_state.force_recommendation_refresh
    
    if (st.session_state.recommendation is None or force_refresh or language_changed):
        st.session_state.recommendation_loading = True
        
        # Prepare user data for the prompt
        personal_info = {
            'age': st.session_state.get('age', 'Not provided'),
            'gender': st.session_state.get('gender', 'Not provided'),
            'height': st.session_state.get('height', 'Not provided'),
            'weight': st.session_state.get('weight', 'Not provided'),
            'exercise_frequency': st.session_state.get('exercise_frequency', 'Not provided'),
            'health_history': st.session_state.get('health_history', 'Not provided')
        }
        
        weather_advice = st.session_state.get('advice', 'Not available')
        tongue_result = st.session_state.get('tongue_analysis_result', st.session_state.get('result', 'Not available'))
        additional_info = st.session_state.get('additional_info', '')
        
        # Create the prompt based on language
        if lang == "ENG":
            user_prompt = f"""Please provide a comprehensive TCM health recommendation based on the following information:

### Weather and Seasonal Factors:
{weather_advice}

### Personal Information:
- Age: {personal_info['age']}
- Gender: {personal_info['gender']}
- Height: {personal_info['height']} cm
- Weight: {personal_info['weight']} kg
- Exercise Frequency: {personal_info['exercise_frequency']} hours per week
- Health History: {personal_info['health_history']}

### Tongue Diagnosis Results:
{tongue_result}

### Additional Information:
{additional_info}

Please structure your response with these sections:
1. Overall Health Assessment
2. Herbal Prescriptions (provide 3 specific formulas with preparation methods and benefits)
3. Dietary Recommendations
4. Lifestyle Adjustments
"""
            system_prompt = """You are a highly experienced TCM practitioner with expertise in integrating various diagnostic methods.
Provide a holistic, personalized health recommendation that considers all provided information, with special focus on:
1. Weather/seasonal influences and their impact on the body's balance
2. Personal physical characteristics and lifestyle factors
3. Tongue diagnosis findings as a key diagnostic indicator
4. Any additional symptoms or concerns mentioned

### Note:
- Ensure your recommendations are comprehensive and specific, including all necessary details.
- More visual recommendations will be easier for users to understand and accept.
- Explain TCM concepts in simple language for non-professionals to understand.

Your response should be comprehensive yet practical, with specific, actionable advice. For herbal prescriptions, include preparation methods, usage instructions, and expected benefits.
Write in a professional but accessible tone, explaining TCM concepts in ways that are understandable to those unfamiliar with traditional medicine."""

        else:
            user_prompt = f"""請根據以下信息提供全面的中醫健康建議：

### 天氣和季節因素：
{weather_advice}

### 個人信息：
- 年齡：{personal_info['age']}
- 性別：{personal_info['gender']}
- 身高：{personal_info['height']} 厘米
- 體重：{personal_info['weight']} 公斤
- 運動頻率：{personal_info['exercise_frequency']} 小時/週
- 健康歷史：{personal_info['health_history']}

### 舌診結果：
{tongue_result}

### 附加信息：
{additional_info}

請按以下結構組織您的回應：
1. 整體健康評估
2. 中藥處方（提供3個特定方劑，包括製備方法和益處）
3. 飲食建議
4. 生活方式調整

"""
            system_prompt = """您是一位經驗豐富的中醫師，擅長整合各種診斷方法。
請提供全面、個性化的健康建議，考慮所有提供的信息，特別關注：
1. 天氣/季節影響及其對身體平衡的影響
2. 個人身體特徵和生活方式因素
3. 舌診發現作為關鍵診斷指標
4. 提到的任何其他症狀或顧慮

您的回應應該既全面又實用，提供具體、可操作的建議。對於中藥處方，包括製備方法、使用說明和預期效果。
以專業但易於理解的語氣撰寫，以易於理解的方式解釋中醫概念。
### 注意：
- 請確保您的建議全面且具體，並包括所有必要的信息。
- 更可視化的建議將更容易被用戶理解和接受。
- 請使用易於理解的語言解釋中醫概念，以便非專業人士也能理解。

"""

        try:
            # Generate the recommendation
            recommendation = advice_llm(system_prompt, user_prompt, model_type="openai")
            
            # Save to session state
            st.session_state.recommendation = recommendation
            st.session_state.recommendation_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Reset the force refresh flag
            if 'force_recommendation_refresh' in st.session_state:
                st.session_state.force_recommendation_refresh = False
                
        except Exception as e:
            st.error(f"Error generating recommendation: {str(e)}")
            st.session_state.recommendation = f"Error: {str(e)}"
        
        st.session_state.recommendation_loading = False
        
    return st.session_state.recommendation

def show_recommendation():
    # Initialize session variables
    if 'additional_info' not in st.session_state:
        st.session_state.additional_info = ""
    if 'language' not in st.session_state:
        st.session_state.language = "ENG"
    if 'recommendation_expanded' not in st.session_state:
        st.session_state.recommendation_expanded = {
            'personal': True,
            'tongue': False,
            'weather': False
        }
    
    lang = st.session_state.language
    
    # Page header
    st.markdown(f"<h1 style='color: #5D5CDE;'>{'Personalized TCM Recommendations' if lang == 'ENG' else '個人化中醫建議'}</h1>", unsafe_allow_html=True)
    
    # Generate recommendation if necessary
    recommendation = llm_recommendation()
    
    # Main layout with two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Recommendation display section
        st.markdown(f"""
            <h3 style="color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                🌿 {'Your Health Recommendations' if lang == 'ENG' else '您的健康建議'}
            </h3>
        """, unsafe_allow_html=True)
        
        # Show loading state or recommendation
        if st.session_state.recommendation_loading:
            st.spinner("Generating personalized recommendations..." if lang == "ENG" else "正在生成個人化建議...")
            
            # Show a progress placeholder while loading
            st.markdown("""
            <div style="background-color: #f8f9fb; border-radius: 8px; padding: 20px; text-align: center;">
                <div style="color: #666; margin: 20px 0;">
                    Analyzing your data and generating personalized recommendations...
                </div>
                <div style="width: 100%; height: 6px; background-color: #eee; border-radius: 3px; overflow: hidden;">
                    <div style="width: 30%; height: 100%; background-color: #5D5CDE; border-radius: 3px; animation: pulse 1.5s infinite;"></div>
                </div>
            </div>
            <style>
                @keyframes pulse {
                    0% { width: 10%; margin-left: 0%; }
                    50% { width: 30%; margin-left: 70%; }
                    100% { width: 10%; margin-left: 0%; }
                }
            </style>
            """, unsafe_allow_html=True)
        elif recommendation:
            # Try to extract prescriptions for special display
            prescriptions = extract_prescriptions(recommendation)
            
            # Format and display the recommendation
            # First check if it contains headers already
            recommendation_html = format_markdown_to_html(recommendation)
            
            # Display the rendered HTML
            st.markdown(recommendation_html, unsafe_allow_html=True)
            
            # Show generation time if available
            if st.session_state.recommendation_time:
                st.markdown(f"""
                <div style="font-size: 12px; color: #888; text-align: right; margin-top: 20px;">
                    {'Generated on: ' if lang == 'ENG' else '生成於：'} {st.session_state.recommendation_time}
                </div>
                """, unsafe_allow_html=True)
            
            # Save/Share and Refresh buttons
            save_col, refresh_col = st.columns([3, 1])
            with save_col:
                if st.button("📄 " + ("Save Recommendations" if lang == "ENG" else "保存建議"), use_container_width=True):
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    filename = f"tcm_recommendation_{timestamp}.txt"
                    
                    # Create a download link for the recommendation
                    def get_download_link(text, filename):
                        b64 = base64.b64encode(text.encode()).decode()
                        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Click here to download</a>'
                        return href
                    
                    download_link = get_download_link(recommendation, filename)
                    st.markdown(f"{'Your recommendation is ready for download:' if lang == 'ENG' else '您的建議已準備好下載：'} {download_link}", unsafe_allow_html=True)
            
            with refresh_col:
                if st.button("🔄 " + ("Refresh" if lang == "ENG" else "刷新"), use_container_width=True):
                    st.session_state.force_recommendation_refresh = True
                    st.rerun()
        else:
            # Show placeholder if no recommendation yet
            st.info("Complete your personal information and tongue diagnosis to receive personalized recommendations." if lang == "ENG" else "完成您的個人信息和舌診以獲取個性化建議。")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Additional information input
        st.markdown(f"""
            <h3 style="color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                ✏️ {'Additional Health Information' if lang == 'ENG' else '其他健康信息'}
            </h3>
        """, unsafe_allow_html=True)
        
        st.markdown(f"{'Share any additional symptoms, concerns, or health goals to receive more personalized recommendations.' if lang == 'ENG' else '分享任何額外症狀、疑慮或健康目標，以獲取更加個性化的建議。'}")
        
        additional_info = st.text_area(
            "Additional Information" if lang == "ENG" else "其他信息",
            value=st.session_state.get('additional_info', ''),
            height=120,
            placeholder="For example: sleep quality, stress levels, digestive issues, pain, energy levels, etc." if lang == "ENG" else "例如：睡眠質量、壓力水平、消化問題、疼痛、能量水平等。"
        )
        if st.button("💬 " + ("Update Recommendations" if lang == "ENG" else "更新建議"), type="primary", use_container_width=True):
            additional_info = st.session_state.get('additional_info', '')
            st.session_state.additional_info = additional_info

            st.session_state.force_recommendation_refresh = True
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Data summary section
        # Personal info card
        with st.expander("👤 " + ("Personal Information" if lang == "ENG" else "個人信息"), expanded=st.session_state.recommendation_expanded['personal']):
            # Check which fields exist and display them nicely
            has_info = False
            
            # Prepare the data to display
            info_fields = [
                {"key": "name", "label": "Name" if lang == "ENG" else "姓名", "icon": "👤"},
                {"key": "age", "label": "Age" if lang == "ENG" else "年齡", "icon": "🔢"},
                {"key": "gender", "label": "Gender" if lang == "ENG" else "性別", "icon": "⚧️"},
                {"key": "height", "label": "Height (cm)" if lang == "ENG" else "身高 (厘米)", "icon": "📏"},
                {"key": "weight", "label": "Weight (kg)" if lang == "ENG" else "體重 (公斤)", "icon": "⚖️"},
                {"key": "exercise_frequency", "label": "Exercise (hrs/week)" if lang == "ENG" else "運動 (小時/週)", "icon": "🏃"},
                {"key": "health_history", "label": "Health History" if lang == "ENG" else "健康歷史", "icon": "📋"}
            ]
            
            # Display each field if it exists
            for field in info_fields:
                if field["key"] in st.session_state and st.session_state[field["key"]]:
                    has_info = True
                    value = st.session_state[field["key"]]
                    
                    # Format display for different field types
                    if field["key"] == "health_history" and value:
                        st.markdown(f"""
                        <div style="margin-bottom: 15px;">
                            <div style="font-size: 15px; font-weight: 500; margin-bottom: 5px;">
                                {field["icon"]} {field["label"]}
                            </div>
                            <div style="padding: 10px; background-color: #f8f9fb; border-radius: 5px; font-size: 14px;">
                                {value}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #eee;">
                            <div>{field["icon"]} {field["label"]}</div>
                            <div style="font-weight: 500;">{value}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            if not has_info:
                st.info("No personal information available" if lang == "ENG" else "沒有可用的個人信息")
        
        # Tongue analysis card
        with st.expander("👅 " + ("Tongue Diagnosis" if lang == "ENG" else "舌診分析"), expanded=st.session_state.recommendation_expanded['tongue']):
            # Check if we have tongue analysis results
            if 'tongue_analysis_result' in st.session_state and st.session_state.tongue_analysis_result:
                # If we have a score, display it
                if 'tongue_analysis_score' in st.session_state and st.session_state.tongue_analysis_score:
                    score = st.session_state.tongue_analysis_score
                    
                    # Determine color based on score
                    if score >= 80:
                        score_color = "#2ecc71"  # Green
                    elif score >= 60:
                        score_color = "#f39c12"  # Orange
                    else:
                        score_color = "#e74c3c"  # Red
                    
                    st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 15px;">
                        <div style="font-size: 14px; margin-bottom: 5px;">{'Health Score' if lang == 'ENG' else '健康評分'}</div>
                        <div style="font-size: 32px; font-weight: bold; color: {score_color};">{score}</div>
                        <div style="width: 100%; height: 8px; background-color: #f1f1f1; border-radius: 4px; margin: 8px 0;">
                            <div style="width: {score}%; height: 100%; border-radius: 4px; background-color: {score_color};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show a summary of the tongue analysis
                st.markdown("**Summary:**" if lang == "ENG" else "**摘要：**")
                
                # Extract key points from the tongue analysis result
                result_text = st.session_state.tongue_analysis_result
                
                # Try to extract the first few lines of each section
                summary_points = []
                
                # Look for tongue body color
                body_color_match = re.search(r'(?:Tongue Body Color|舌體顏色)[^\n]*\n([^\n#]+)', result_text, re.IGNORECASE)
                if body_color_match:
                    summary_points.append(f"🟠 {'Body: ' if lang == 'ENG' else '舌體：'}{body_color_match.group(1).strip()}")
                
                # Look for tongue coating
                coating_match = re.search(r'(?:Tongue Coating|舌苔)[^\n]*\n([^\n#]+)', result_text, re.IGNORECASE)
                if coating_match:
                    summary_points.append(f"⚪ {'Coating: ' if lang == 'ENG' else '舌苔：'}{coating_match.group(1).strip()}")
                
                # Look for tongue shape
                shape_match = re.search(r'(?:Tongue Shape|舌形)[^\n]*\n([^\n#]+)', result_text, re.IGNORECASE)
                if shape_match:
                    summary_points.append(f"📏 {'Shape: ' if lang == 'ENG' else '舌形：'}{shape_match.group(1).strip()}")
                
                # Display the summary points
                if summary_points:
                    for point in summary_points:
                        st.markdown(point)
                else:
                    # If we couldn't extract structured points, just show a general message
                    st.info("Tongue analysis available in full recommendation" if lang == "ENG" else "完整建議中提供舌診分析")
                
                # Link to full analysis
                st.markdown(f"[{'See full tongue analysis' if lang == 'ENG' else '查看完整舌診分析'}](#)")
            elif 'result' in st.session_state and st.session_state.result:
                # For backward compatibility with the old "result" key
                st.markdown(f"{'Tongue analysis is available' if lang == 'ENG' else '舌診分析可用'}")
            else:
                st.info("No tongue diagnosis available" if lang == "ENG" else "沒有可用的舌診")
        
        # Weather/seasonal info card
        with st.expander("🌤️ " + ("Weather & Seasonal Factors" if lang == "ENG" else "天氣和季節因素"), expanded=st.session_state.recommendation_expanded['weather']):
            if 'advice' in st.session_state and st.session_state.advice:
                # Try to extract key seasonal advice
                advice_text = st.session_state.advice
                
                # First try to get any "what to be mindful of" section
                mindful_match = re.search(r'(?:What should I be mindful of today:|今天應該注意什麼：)(.*?)(?:Traditional Chinese Medicine prescription:|中藥處方：|$)', advice_text, re.DOTALL)
                
                if mindful_match:
                    mindful_text = mindful_match.group(1).strip()
                    
                    # Try to extract bullet points or numbered items
                    items = re.findall(r'(?:^|\n)(?:\d+\.|\*|\-)\s*([^\n]+)', mindful_text)
                    
                    if items:
                        st.markdown("**Seasonal Health Tips:**" if lang == "ENG" else "**季節健康提示：**")
                        for item in items[:3]:  # Show up to 3 items
                            st.markdown(f"• {item.strip()}")
                    else:
                        # Just show the first paragraph
                        paragraphs = mindful_text.split("\n\n")
                        if paragraphs:
                            st.markdown(paragraphs[0])
                else:
                    # If no structured format, just show first part of advice
                    parts = advice_text.split("\n\n")
                    if parts:
                        st.markdown(parts[0][:200] + "..." if len(parts[0]) > 200 else parts[0])
                
                # Show lunar calendar info if available
                if 'lunar_info' in st.session_state and st.session_state.lunar_info:
                    lunar_info = st.session_state.lunar_info
                    
                    st.markdown("""
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**{'Lunar Calendar' if lang == 'ENG' else '農曆日期'}:** {lunar_info.get('lunar_year', '')}, {lunar_info.get('lunar_date', '')}")
                    
                    if 'zodiac_eng' in lunar_info:
                        zodiac = lunar_info['zodiac_eng'] if lang == 'ENG' else lunar_info['zodiac_chi']
                        st.markdown(f"**{'Zodiac' if lang == 'ENG' else '生肖'}:** {zodiac}")
            else:
                st.info("No seasonal information available" if lang == "ENG" else "沒有可用的季節信息")
    
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
            
            div[style*="background-color: #f8f9fb"] {
                background-color: #3d3d3d !important;
            }
            
            h3[style*="color: #333"], h4 {
                color: #e0e0e0 !important;
                border-bottom-color: #444 !important;
            }
            
            div[style*="color: #666"], div[style*="color: #333"], div[style*="color: #888"] {
                color: #e0e0e0 !important;
            }
            
            div[style*="border-bottom: 1px solid #eee"] {
                border-bottom-color: #444 !important;
            }
            
            div[style*="border-top: 1px solid #eee"] {
                border-top-color: #444 !important;
            }
            
            div[style*="background-color: #f1f1f1"] {
                background-color: #444 !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)