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
import io
import streamlit as st
import re
import os

join = os.path.join
import base64
import time
from datetime import datetime
from PIL import Image
import requests
from llm_openai import advice_llm

def show_quick_start(client, model_name):
    """
    A quick start wizard to guide users through the essential steps
    for generating a personalized TCM recommendation.
    """
    lang = st.session_state.language
    step = st.session_state.quick_start_step
    
    # Page header
    st.markdown(f"<h1 style='color: #5D5CDE;'>{'Quick Start Guide' if lang == 'ENG' else '快速入門指南'}</h1>", unsafe_allow_html=True)
    
    # Progress bar
    progress_percentage = (step - 1) / 4 * 100  # 4 steps total
    st.progress(progress_percentage / 100)
    
    # Step indicator using Streamlit columns
    steps = ["Personal Info", "Tongue Analysis", "Weather & Season", "Recommendations"] if lang == "ENG" else ["個人信息", "舌診分析", "天氣與季節", "推薦"]
    
    # Create columns for each step
    cols = st.columns(len(steps))
    
    # Display each step with appropriate styling
    for i, (col, step_name) in enumerate(zip(cols, steps)):
        step_num = i + 1
        
        # Determine step status
        if step_num < step:
            status = "complete"
            icon = "✅"
            color = "#2ecc71"  # Green for completed
        elif step_num == step:
            status = "current"
            icon = "➡️"
            color = "#5D5CDE"  # Purple for current
        else:
            status = "pending"
            icon = "○"
            color = "#ccc"  # Gray for pending
        
        # Use Streamlit's markdown to display the step with proper styling
        with col:
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<div style='color: {color}; font-weight: {'bold' if status == 'current' else 'normal'};'>"
                f"{icon} {step_name}"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    
    # Add a separator after the step indicator
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Display current step content
    if step == 1:
        show_quick_start_personal_info()
    elif step == 2:
        show_quick_start_tongue_analysis(client, model_name)
    elif step == 3:
        show_quick_start_weather()
    elif step == 4:
        show_quick_start_recommendation(client, model_name)
    elif step == 5:
        show_quick_start_complete()

def show_quick_start_personal_info():
    """Step 1: Collect basic personal information with elderly-friendly, interactive inputs"""
    lang = st.session_state.language
    
    # Main header with custom styling
    st.markdown(f"""
    <div style="background: linear-gradient(to right, #5D5CDE, #8583E1); padding: 20px; border-radius: 10px; margin-bottom: 25px;">
        <h2 style="color: white; margin-bottom: 10px;">{'Step 1: Tell us about yourself' if lang == 'ENG' else '步驟1：告訴我們關於您的信息'}</h2>
        <p style="color: rgba(255, 255, 255, 0.9); font-size: 16px;">{'We need some basic information to provide personalized TCM recommendations.' if lang == 'ENG' else '我們需要一些基本信息來提供個性化的中醫建議。'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize the personal info step tracker if not already set
    if 'personal_info_step' not in st.session_state:
        st.session_state.personal_info_step = 1
    
    # Total number of personal info questions
    total_steps = 5
    
    # Custom CSS for elder-friendly UI
    st.markdown("""
    <style>
    /* Large buttons for easier tapping */
    .large-button {
        padding: 15px !important;
        font-size: 18px !important;
        border-radius: 8px !important;
        min-height: 60px !important;
    }
    
    /* Larger text and controls */
    .elder-friendly label, .elder-friendly div {
        font-size: 18px !important;
    }
    
    /* Colorful, larger selection buttons */
    .selection-button {
        display: block;
        background-color: #f8f9fa;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 18px;
    }
    .selection-button:hover {
        background-color: #f0f0f0;
        border-color: #d0d0d0;
    }
    .selection-button.selected {
        background-color: rgba(93, 92, 222, 0.15);
        border-color: #5D5CDE;
        font-weight: bold;
    }
    
    /* Custom slider styling */
    .custom-slider {
        padding: 25px 0px 35px 0px;
    }
    .custom-slider .stSlider {
        height: 25px !important;
    }
    .custom-slider p {
        font-size: 16px !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Large, clear step indicators with both text and numbers
    step_titles = [
        ("Personal", "個人資料"),
        ("Age & Gender", "年齡和性別"),
        ("Body Stats", "身體數據"),
        ("Exercise", "運動"),
        ("Health", "健康")
    ]
    
    # Display step indicator
    st.markdown(f"""
    <div style="margin-bottom: 30px; text-align: center;">
        <h3 style="color: #5D5CDE; font-size: 24px; margin-bottom: 5px;">
            {f"Step {st.session_state.personal_info_step} of {total_steps}" if lang == "ENG" else f"步驟 {st.session_state.personal_info_step} / {total_steps}"}
        </h3>
        <div style="font-size: 20px; font-weight: bold; color: #333;">
            {step_titles[st.session_state.personal_info_step-1][0] if lang == "ENG" else step_titles[st.session_state.personal_info_step-1][1]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display progress bar
    sub_progress = st.session_state.personal_info_step / total_steps
    st.progress(sub_progress)
    
    # Step 1: Name with large buttons for common names
    if st.session_state.personal_info_step == 1:
        st.markdown(f"""
        <h3 style="color: #5D5CDE; margin: 20px 0; font-size: 22px; text-align: center;">
            {'What is your name?' if lang == 'ENG' else '您的名字是什麼？'}
        </h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # Or allow custom name input with larger text field
            st.markdown("<p style='text-align: center; margin-top: 20px;'></p>", unsafe_allow_html=True)
            name = st.text_input(
                "Name" if lang == "ENG" else "姓名", 
                value=st.session_state.get('name', ''),
                placeholder="Your name" if lang == "ENG" else "您的姓名",
                label_visibility="collapsed",
                key="name_large"
            )
            
            # Large, clearly labeled buttons
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            
            if st.button(
                "Next ➡️" if lang == "ENG" else "下一步 ➡️", 
                type="primary",
                use_container_width=True,
                key="name_next"
            ):
                st.session_state.name = name
                st.session_state.personal_info_step = 2
                st.rerun()
            
            if st.button(
                "Skip All" if lang == "ENG" else "跳過全部", 
                type="secondary",
                use_container_width=True,
                key="skip_all_personal"
            ):
                st.session_state.personal_data_complete = True
                st.session_state.quick_start_step = 2
                st.rerun()
    
    # Step 2: Age and Gender with tap interface rather than typing
    elif st.session_state.personal_info_step == 2:
        st.markdown(f"""
        <h3 style="color: #5D5CDE; margin: 20px 0; font-size: 22px; text-align: center;">
            {'What is your age and gender?' if lang == 'ENG' else '您的年齡和性別是？'}
        </h3>
        """, unsafe_allow_html=True)
        
        # Age selection with visual buttons for age ranges
        st.markdown(f"""
        <p style="font-weight: 500; font-size: 18px; margin-bottom: 15px;">
            {'Select your age range:' if lang == 'ENG' else '選擇您的年齡範圍:'}
        </p>
        """, unsafe_allow_html=True)
        
        # Age ranges as clickable buttons
        age_ranges = ["Under 18", "18-30", "31-45", "46-60", "61-75", "Over 75"] if lang == "ENG" else [
            "18歲以下", "18-30歲", "31-45歲", "46-60歲", "61-75歲", "75歲以上"
        ]
        
        # Create a layout with 3 buttons per row
        for i in range(0, len(age_ranges), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(age_ranges):
                    with cols[j]:
                        age_range = age_ranges[i + j]
                        if st.button(
                            age_range, 
                            key=f"age_range_{i+j}",
                            use_container_width=True,
                        ):
                            # Map age ranges to representative values
                            age_map = {
                                0: 16, 1: 25, 2: 38, 3: 53, 4: 68, 5: 80
                            }
                            st.session_state.age = age_map[i + j]
                            
                            # Show exact age refinement with a slider
                            st.session_state.show_age_slider = True
                            st.rerun()
        
        # Show the slider if button was clicked
        if st.session_state.get('show_age_slider', False):
            st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)
            
            if st.session_state.age < 18:
                min_age, max_age = 1, 18
            elif st.session_state.age <= 30:
                min_age, max_age = 18, 30
            elif st.session_state.age <= 45:
                min_age, max_age = 31, 45
            elif st.session_state.age <= 60:
                min_age, max_age = 46, 60
            elif st.session_state.age <= 75:
                min_age, max_age = 61, 75
            else:
                min_age, max_age = 75, 100
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <p style="text-align: center; font-weight: 500; font-size: 18px; margin-bottom: 10px;">
                    {'Refine your age:' if lang == 'ENG' else '精確您的年齡:'}
                </p>
                """, unsafe_allow_html=True)
                
                # Display current age in big digits
                st.markdown(f"""
                <div style="text-align: center; font-size: 48px; font-weight: bold; color: #5D5CDE; margin: 10px 0;">
                    {st.session_state.age}
                </div>
                """, unsafe_allow_html=True)
                
                # Large, clickable age adjustment buttons
                age_col1, age_col2, age_col3 = st.columns([1, 1, 1])
                with age_col1:
                    if st.button("➖", key="age_minus", use_container_width=True):
                        if st.session_state.age > min_age:
                            st.session_state.age -= 1
                            st.rerun()
                
                with age_col3:
                    if st.button("➕", key="age_plus", use_container_width=True):
                        if st.session_state.age < max_age:
                            st.session_state.age += 1
                            st.rerun()
        
        # Divider
        st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
        
        # Gender selection with visual icons
        st.markdown(f"""
        <p style="font-weight: 500; font-size: 18px; margin-bottom: 15px;">
            {'Select your gender:' if lang == 'ENG' else '選擇您的性別:'}
        </p>
        """, unsafe_allow_html=True)
        
        # Large, icon-based gender selection buttons
        gen_col1, gen_col2, gen_col3 = st.columns([1, 1, 1])
        
        with gen_col1:
            if st.button(
                "♂️ " + ("Male" if lang == "ENG" else "男性"),
                key="gender_male",
                use_container_width=True,
            ):
                st.session_state.gender = "M"
        
        with gen_col2:
            if st.button(
                "♀️ " + ("Female" if lang == "ENG" else "女性"),
                key="gender_female",
                use_container_width=True,
            ):
                st.session_state.gender = "F"
                
        with gen_col3:
            if st.button(
                "⚪ " + ("Other" if lang == "ENG" else "其他"),
                key="gender_other",
                use_container_width=True,
            ):
                st.session_state.gender = "---"
        
        # Display current selections
        if st.session_state.get('age', 0) > 0 or st.session_state.get('gender', '') != '':
            st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)
            
            age_display = str(st.session_state.get('age', '')) if st.session_state.get('age', 0) > 0 else "Not set"
            gender_display = {"M": "Male", "F": "Female", "---": "Other"}.get(st.session_state.get('gender', ''), "Not set") if lang == "ENG" else {
                "M": "男性", "F": "女性", "---": "其他"
            }.get(st.session_state.get('gender', ''), "未設置")
            
            st.markdown(f"""
            <div style="background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 20px; text-align: center;">
                <p style="font-size: 18px; margin-bottom: 10px;">
                    {'Your selections:' if lang == 'ENG' else '您的選擇:'}
                </p>
                <div style="display: flex; justify-content: center; gap: 40px;">
                    <div>
                        <div style="font-weight: bold; color: #5D5CDE;">{'Age' if lang == 'ENG' else '年齡'}</div>
                        <div style="font-size: 20px;">{age_display}</div>
                    </div>
                    <div>
                        <div style="font-weight: bold; color: #5D5CDE;">{'Gender' if lang == 'ENG' else '性別'}</div>
                        <div style="font-size: 20px;">{gender_display}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(
                "⬅️ " + ("Back" if lang == "ENG" else "返回"), 
                type="secondary",
                use_container_width=True,
                key="age_back"
            ):
                st.session_state.personal_info_step = 1
                st.rerun()
        
        with col3:
            if st.button(
                "Next ➡️" if lang == "ENG" else "下一步 ➡️", 
                type="primary",
                use_container_width=True,
                key="age_next"
            ):
                st.session_state.personal_info_step = 3
                st.rerun()
        
        with col2:
            if st.button(
                "Skip" if lang == "ENG" else "跳過", 
                type="secondary",
                use_container_width=True,
                key="age_skip"
            ):
                st.session_state.personal_info_step = 3
                st.rerun()
    
    # Step 3: Height and Weight with sliders instead of number inputs
    elif st.session_state.personal_info_step == 3:
        st.markdown(f"""
        <h3 style="color: #5D5CDE; margin: 20px 0; font-size: 22px; text-align: center;">
            {'What is your height and weight?' if lang == 'ENG' else '您的身高和體重是？'}
        </h3>
        """, unsafe_allow_html=True)
        
        # Height with quick options plus slider
        st.markdown(f"""
        <p style="font-weight: 500; font-size: 18px; margin-bottom: 15px;">
            {'Your height:' if lang == 'ENG' else '您的身高:'}
        </p>
        """, unsafe_allow_html=True)
        
        # Common height ranges as buttons
        height_ranges = [
            ("Under 160cm", "160cm以下"),
            ("160-170cm", "160-170cm"),
            ("170-180cm", "170-180cm"),
            ("Over 180cm", "180cm以上")
        ]
        
        height_cols = st.columns(len(height_ranges))
        for i, (height_eng, height_chi) in enumerate(height_ranges):
            with height_cols[i]:
                if st.button(
                    height_eng if lang == "ENG" else height_chi,
                    key=f"height_range_{i}",
                    use_container_width=True
                ):
                    # Set initial height value based on selection
                    height_values = [155, 165, 175, 185]
                    st.session_state.height = height_values[i]
                    st.session_state.show_height_slider = True
                    st.rerun()
        
        # Height slider for precise adjustment
        if 'show_height_slider' not in st.session_state:
            st.session_state.show_height_slider = False
            
        if st.session_state.show_height_slider or st.session_state.get('height', 0) > 0:
            st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)
            
            # Determine slider range based on selection
            if st.session_state.get('height', 0) <= 160:
                min_height, max_height = 140, 160
            elif st.session_state.get('height', 0) <= 170:
                min_height, max_height = 160, 170
            elif st.session_state.get('height', 0) <= 180:
                min_height, max_height = 170, 180
            else:
                min_height, max_height = 180, 210
                
            # Center the display and make it larger
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Display current height in big digits
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 15px;">
                    <div style="font-size: 36px; font-weight: bold; color: #5D5CDE;">
                        {st.session_state.get('height', 0)} cm
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Height slider
                height = st.slider(
                    "Height adjustment" if lang == "ENG" else "身高調整",
                    min_value=min_height,
                    max_value=max_height,
                    value=st.session_state.get('height', min_height),
                    step=1,
                    label_visibility="collapsed",
                    key="height_slider"
                )
                st.session_state.height = height
                
        # Divider
        st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
        
        # Weight with quick options plus slider
        st.markdown(f"""
        <p style="font-weight: 500; font-size: 18px; margin-bottom: 15px;">
            {'Your weight:' if lang == 'ENG' else '您的體重:'}
        </p>
        """, unsafe_allow_html=True)
        
        # Common weight ranges as buttons
        weight_ranges = [
            ("Under 50kg", "50kg以下"),
            ("50-65kg", "50-65kg"),
            ("65-80kg", "65-80kg"),
            ("Over 80kg", "80kg以上")
        ]
        
        weight_cols = st.columns(len(weight_ranges))
        for i, (weight_eng, weight_chi) in enumerate(weight_ranges):
            with weight_cols[i]:
                if st.button(
                    weight_eng if lang == "ENG" else weight_chi,
                    key=f"weight_range_{i}",
                    use_container_width=True
                ):
                    # Set initial weight value based on selection
                    weight_values = [45, 58, 72, 85]
                    st.session_state.weight = weight_values[i]
                    st.session_state.show_weight_slider = True
                    st.rerun()
        
        # Weight slider for precise adjustment
        if 'show_weight_slider' not in st.session_state:
            st.session_state.show_weight_slider = False
            
        if st.session_state.show_weight_slider or st.session_state.get('weight', 0) > 0:
            st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)
            
            # Determine slider range based on selection
            if st.session_state.get('weight', 0) < 50:
                min_weight, max_weight = 30, 50
            elif st.session_state.get('weight', 0) < 65:
                min_weight, max_weight = 50, 65
            elif st.session_state.get('weight', 0) < 80:
                min_weight, max_weight = 65, 80
            else:
                min_weight, max_weight = 80, 150
                
            # Center the display and make it larger
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Display current weight in big digits
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 15px;">
                    <div style="font-size: 36px; font-weight: bold; color: #5D5CDE;">
                        {st.session_state.get('weight', 0)} kg
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Weight slider
                weight = st.slider(
                    "Weight adjustment" if lang == "ENG" else "體重調整",
                    min_value=float(min_weight),
                    max_value=float(max_weight),
                    value=float(st.session_state.get('weight', min_weight)),
                    step=0.5,
                    label_visibility="collapsed",
                    key="weight_slider"
                )
                st.session_state.weight = weight
        
        # Calculate BMI if we have height and weight
        # For the BMI display section in Step 3, replace the existing code with this:

        # Calculate BMI if we have height and weight
        if st.session_state.get('height', 0) > 0 and st.session_state.get('weight', 0) > 0:
            height = st.session_state.height
            weight = st.session_state.weight
            
            bmi = round(weight / ((height/100) ** 2), 1)
            
            # Determine BMI category and color
            if bmi < 18.5:
                bmi_category = "Underweight" if lang == "ENG" else "體重過輕"
                bmi_color = "#3498db"  # Blue
                bmi_percentage = max(min(bmi / 18.5 * 50, 50), 10)  # Scale to 0-50% range
            elif bmi < 24:
                bmi_category = "Normal" if lang == "ENG" else "正常"
                bmi_color = "#2ecc71"  # Green
                bmi_percentage = 50 + ((bmi - 18.5) / (24 - 18.5) * 20)  # Scale to 50-70% range
            elif bmi < 27:
                bmi_category = "Overweight" if lang == "ENG" else "過重"
                bmi_color = "#f39c12"  # Orange
                bmi_percentage = 70 + ((bmi - 24) / (27 - 24) * 10)  # Scale to 70-80% range
            elif bmi < 30:
                bmi_category = "Mild Obesity" if lang == "ENG" else "輕度肥胖"
                bmi_color = "#e67e22"  # Dark Orange
                bmi_percentage = 80 + ((bmi - 27) / (30 - 27) * 10)  # Scale to 80-90% range
            elif bmi < 35:
                bmi_category = "Moderate Obesity" if lang == "ENG" else "中度肥胖"
                bmi_color = "#e74c3c"  # Red
                bmi_percentage = 90 + ((bmi - 30) / (35 - 30) * 5)  # Scale to 90-95% range
            else:
                bmi_category = "Severe Obesity" if lang == "ENG" else "重度肥胖"
                bmi_color = "#c0392b"  # Dark Red
                bmi_percentage = 95 + min((bmi - 35) / 15 * 5, 5)  # Scale to 95-100% range, cap at 100%
            
            # Display enhanced BMI widget using separate components instead of complex HTML
            st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)
            
            # Container for BMI display
            st.markdown(f"""
            <div style=" border-radius: 12px; padding: 20px; margin: 20px 0; text-align: left;">
                <div style="font-weight: bold; margin-bottom: 15px; font-size: 20px; color: #333;">
                    {'Your BMI' if lang == 'ENG' else '您的BMI:'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show BMI score as large text
            st.markdown(f"<h1 style='text-align: center; color: {bmi_color}; font-size: 48px;'>{bmi}</h1>", unsafe_allow_html=True)
            
            # Show BMI category
            st.markdown(f"<h3 style='text-align: center; color: {bmi_color}; margin-bottom: 20px;'>{bmi_category}</h3>", unsafe_allow_html=True)
            
            # Create a progress bar component
            st.progress(bmi_percentage/100)
            
            # Show BMI scale labels
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("<div style='text-align: left; font-size: 14px; color: #666;'>Underweight</div>" if lang == "ENG" else "<div style='text-align: left; font-size: 14px; color: #666;'>體重過輕</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='text-align: center; font-size: 14px; color: #666;'>Normal</div>" if lang == "ENG" else "<div style='text-align: center; font-size: 14px; color: #666;'>正常</div>", unsafe_allow_html=True)
            with col3:
                st.markdown("<div style='text-align: center; font-size: 14px; color: #666;'>Overweight</div>" if lang == "ENG" else "<div style='text-align: center; font-size: 14px; color: #666;'>過重</div>", unsafe_allow_html=True)
            with col4:
                st.markdown("<div style='text-align: right; font-size: 14px; color: #666;'>Obesity</div>" if lang == "ENG" else "<div style='text-align: right; font-size: 14px; color: #666;'>肥胖</div>", unsafe_allow_html=True)
            
            # Add TCM context
            st.markdown(f"""
            <br>
            <div style="text-align: center; font-size: 16px; color: #666; margin-top: 15px;">
                {'In TCM, your BMI helps determine your body constitution type.' if lang == 'ENG' else '在中醫中，BMI有助於確定您的體質類型。'}
            </div><br><br>
            """, unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(
                "⬅️ " + ("Back" if lang == "ENG" else "返回"), 
                type="secondary",
                use_container_width=True,
                key="height_back"
            ):
                st.session_state.personal_info_step = 2
                st.rerun()
        
        with col3:
            if st.button(
                "Next ➡️" if lang == "ENG" else "下一步 ➡️", 
                type="primary",
                use_container_width=True,
                key="height_next"
            ):
                st.session_state.personal_info_step = 4
                st.rerun()
        
        with col2:
            if st.button(
                "Skip" if lang == "ENG" else "跳過", 
                type="secondary",
                use_container_width=True,
                key="height_skip"
            ):
                st.session_state.personal_info_step = 4
                st.rerun()
    
    # Step 4: Exercise frequency with visual selection
    elif st.session_state.personal_info_step == 4:
        st.markdown(f"""
        <h3 style="color: #5D5CDE; margin: 20px 0; font-size: 22px; text-align: center;">
            {'How often do you exercise?' if lang == 'ENG' else '您多久運動一次？'}
        </h3>
        <p style="text-align: center; margin-bottom: 25px; font-size: 16px; color: #666;">
            {'Tap on the option that best describes your exercise routine.' if lang == 'ENG' else '點選最符合您運動習慣的選項。'}
        </p>
        """, unsafe_allow_html=True)
        
        # Exercise options with icons and descriptions
        exercise_options = [
            {
                "icon": "🛋️",
                "title_eng": "Rarely exercise",
                "title_chi": "很少運動",
                "desc_eng": "Little to no physical activity",
                "desc_chi": "很少或沒有體力活動",
                "value": "0"
            },
            {
                "icon": "🚶",
                "title_eng": "Light exercise",
                "title_chi": "輕度運動",
                "desc_eng": "1-2 hours weekly (walking, etc.)",
                "desc_chi": "每週1-2小時（散步等）",
                "value": "1-2"
            },
            {
                "icon": "🏊",
                "title_eng": "Moderate exercise",
                "title_chi": "中度運動",
                "desc_eng": "3-4 hours weekly",
                "desc_chi": "每週3-4小時",
                "value": "3-4"
            },
            {
                "icon": "🏃",
                "title_eng": "Regular exercise",
                "title_chi": "規律運動",
                "desc_eng": "5-6 hours weekly",
                "desc_chi": "每週5-6小時",
                "value": "5-6"
            },
            {
                "icon": "🏋️",
                "title_eng": "Intensive exercise",
                "title_chi": "強度運動",
                "desc_eng": "7+ hours weekly",
                "desc_chi": "每週7小時以上",
                "value": ">7"
            }
        ]
        
        # Display each option as a clickable button
        for i, option in enumerate(exercise_options):
            # Check if this option is currently selected
            is_selected = st.session_state.get('exercise_frequency', '') == option['value']
            
            # Set button style to primary if selected, otherwise secondary
            button_type = "primary" if is_selected else "secondary"
            
            # Create a single button for each option
            if st.button(
                f"{option['icon']} {option['title_eng'] if lang == 'ENG' else option['title_chi']} - {option['desc_eng'] if lang == 'ENG' else option['desc_chi']}",
                key=f"exercise_option_{i}",
                type=button_type,
                use_container_width=True
            ):
                st.session_state.exercise_frequency = option['value']
                st.rerun()
        
        # TCM exercise tip
        st.markdown(f"""
        <div style="background-color: #f0f4fa; border-radius: 10px; padding: 15px; margin: 20px 0; border-left: 4px solid #5D5CDE;">
            <div style="font-weight: 500; margin-bottom: 8px; color: #5D5CDE; font-size: 16px;">
                {'TCM Tip' if lang == 'ENG' else '中醫小貼士'}
            </div>
            <div style="font-size: 14px; color: #333;">
                {'In Traditional Chinese Medicine, moderate exercise helps balance qi flow and supports overall wellness.' if lang == 'ENG' else '在中醫學中，適度運動有助於平衡氣流並支持整體健康。'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(
                "⬅️ " + ("Back" if lang == "ENG" else "返回"), 
                type="secondary",
                use_container_width=True,
                key="exercise_back"
            ):
                st.session_state.personal_info_step = 3
                st.rerun()
        
        with col3:
            if st.button(
                "Next ➡️" if lang == "ENG" else "下一步 ➡️", 
                type="primary",
                use_container_width=True,
                key="exercise_next"
            ):
                st.session_state.personal_info_step = 5
                st.rerun()
        
        with col2:
            if st.button(
                "Skip" if lang == "ENG" else "跳過", 
                type="secondary",
                use_container_width=True,
                key="exercise_skip"
            ):
                st.session_state.personal_info_step = 5
                st.rerun()
    
    # Step 5: Health history with improved button-based selection
    elif st.session_state.personal_info_step == 5:
        st.markdown(f"""
        <h3 style="color: #5D5CDE; margin: 20px 0; font-size: 22px; text-align: center;">
            {'Do you have any health conditions?' if lang == 'ENG' else '您是否有任何健康狀況？'}
        </h3>
        <p style="text-align: center; margin-bottom: 25px; font-size: 16px; color: #666;">
            {'Tap on all conditions that apply to you.' if lang == 'ENG' else '點選所有適用於您的情況。'}
        </p>
        """, unsafe_allow_html=True)
        
        # Initialize selected conditions if needed
        if 'selected_conditions' not in st.session_state:
            st.session_state.selected_conditions = []
        
        # Common health conditions with icons
        conditions = [
            {"icon": "❤️", "name_eng": "Blood Pressure Issues", "name_chi": "血壓問題"},
            {"icon": "🍬", "name_eng": "Diabetes", "name_chi": "糖尿病"},
            {"icon": "🤧", "name_eng": "Allergies", "name_chi": "過敏"},
            {"icon": "😴", "name_eng": "Sleep Issues", "name_chi": "睡眠問題"},
            {"icon": "🍽️", "name_eng": "Digestive Issues", "name_chi": "消化問題"},
            {"icon": "🦴", "name_eng": "Joint Pain", "name_chi": "關節疼痛"},
            {"icon": "🧠", "name_eng": "Headaches", "name_chi": "頭痛"},
            {"icon": "😰", "name_eng": "Stress/Anxiety", "name_chi": "壓力/焦慮"},
            {"icon": "🫁", "name_eng": "Respiratory Issues", "name_chi": "呼吸問題"},
            {"icon": "⚡", "name_eng": "Fatigue", "name_chi": "疲勞"},
            {"icon": "🔄", "name_eng": "Menstrual Issues", "name_chi": "月經問題"},
            {"icon": "🌡️", "name_eng": "Body Temperature Issues", "name_chi": "體溫問題"}
        ]
        
        # Arrange conditions in a grid with Streamlit columns
        num_cols = 2
        rows = [conditions[i:i+num_cols] for i in range(0, len(conditions), num_cols)]
        
        for row in rows:
            cols = st.columns(num_cols)
            for i, condition in enumerate(row):
                condition_name = condition["name_eng"] if lang == "ENG" else condition["name_chi"]
                
                # Check if this condition is already selected
                is_selected = condition_name in st.session_state.selected_conditions
                
                # Set button style based on selection state
                button_type = "primary" if is_selected else "secondary"
                display_text = f"{condition['icon']} {condition_name}"
                
                with cols[i]:
                    if st.button(
                        display_text,
                        key=f"condition_{condition_name}",
                        type=button_type,
                        use_container_width=True
                    ):
                        # Toggle selection
                        if condition_name in st.session_state.selected_conditions:
                            st.session_state.selected_conditions.remove(condition_name)
                        else:
                            st.session_state.selected_conditions.append(condition_name)
                        st.rerun()
        
        # Display selection summary if any conditions are selected
        if st.session_state.selected_conditions:
            st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background-color: rgba(93, 92, 222, 0.1); border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                <div style="font-weight: 500; margin-bottom: 10px; color: #5D5CDE; font-size: 16px;">
                    {'Selected conditions:' if lang == 'ENG' else '已選擇的狀況:'}
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            """, unsafe_allow_html=True)
            
            for condition in st.session_state.selected_conditions:
                st.markdown(f"""
                    <div style="background-color: #5D5CDE; color: white; border-radius: 20px; padding: 5px 12px; font-size: 14px;">
                        {condition}
                    </div>
                    <br>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Option to add other conditions
        st.markdown(f"""
        <p style="font-weight: 500; margin: 25px 0 15px 0; font-size: 16px;">
            {'Any other health conditions or medications?' if lang == 'ENG' else '任何其他健康狀況或藥物？'}
        </p>
        """, unsafe_allow_html=True)
        
        # Default text includes already selected conditions
        default_text = st.session_state.get('health_history', '')
        if not default_text and st.session_state.selected_conditions:
            default_text = ", ".join(st.session_state.selected_conditions)
        
        health_history = st.text_area(
            "Additional health information" if lang == "ENG" else "其他健康信息", 
            value=default_text,
            placeholder="List any additional health conditions, allergies, or medications..." if lang == "ENG" else "列出任何其他健康狀況，過敏或藥物...",
            height=100,
            label_visibility="collapsed",
            key="health_history_large"
        )
        
        # Data privacy note with large, reassuring icon
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin-top: 20px; font-size: 14px; color: #666; display: flex; align-items: center;">
            <div style="font-size: 32px; margin-right: 15px;">🔒</div>
            <div>
                {'Your health information is kept private and is only used to provide personalized TCM recommendations.' if lang == 'ENG' else '您的健康信息保持私密，僅用於提供個性化的中醫建議。'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(
                "⬅️ " + ("Back" if lang == "ENG" else "返回"), 
                type="secondary",
                use_container_width=True,
                key="history_back"
            ):
                st.session_state.personal_info_step = 4
                st.rerun()
        
        with col2:
            if st.button(
                "Complete & Continue ➡️" if lang == "ENG" else "完成並繼續 ➡️", 
                type="primary",
                use_container_width=True,
                key="history_complete"
            ):
                # Include selected conditions in health history
                if st.session_state.selected_conditions and not health_history:
                    health_history = ", ".join(st.session_state.selected_conditions)
                elif st.session_state.selected_conditions and health_history:
                    # Add selected conditions if they're not already mentioned
                    for condition in st.session_state.selected_conditions:
                        if condition not in health_history:
                            health_history = condition + ", " + health_history
                
                st.session_state.health_history = health_history
                st.session_state.personal_data_complete = True
                st.session_state.quick_start_step = 2
                st.rerun()

def show_quick_start_tongue_analysis(client, model_name):
    """Step 2: Simplified tongue image capture using only camera"""
    lang = st.session_state.language
    
    st.markdown(f"""
    <h2 style='color: #5D5CDE; margin-bottom: 20px;'>{'Step 2: Tongue Diagnosis' if lang == 'ENG' else '步驟2：舌診分析'}</h2>
    <p style='margin-bottom: 20px;'>{'Take a photo of your tongue for AI-powered TCM diagnosis. This helps us understand your internal health conditions.' if lang == 'ENG' else '拍攝您舌頭的照片，以進行AI驅動的中醫診斷。這有助於我們了解您的內部健康狀況。'}</p>
    """, unsafe_allow_html=True)
    
    # Initialize key session variables if they don't exist
    if 'tongue_analysis_result' not in st.session_state:
        st.session_state.tongue_analysis_result = None
    if 'tongue_analysis_score' not in st.session_state:
        st.session_state.tongue_analysis_score = None
    if 'tongue_analysis_loading' not in st.session_state:
        st.session_state.tongue_analysis_loading = False
    
    # Main layout with camera in the center
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3>📸 Align your tongue in the center of the frame</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Display results if already analyzed
    if st.session_state.tongue_analysis_result:
        # Show image if captured
        if 'captured_image' in st.session_state and st.session_state.captured_image is not None:
            st.image(st.session_state.captured_image, caption="Captured tongue image", use_container_width=True)
        
        # Show health score
        score = st.session_state.tongue_analysis_score if st.session_state.tongue_analysis_score else 70
        
        # Determine color based on score
        if score >= 80:
            score_color = "#2ecc71"  # Green
        elif score >= 60:
            score_color = "#f39c12"  # Orange
        else:
            score_color = "#e74c3c"  # Red
        
        # Display score gauge
        st.markdown(f"""
        <div style="text-align: center; margin: 25px 0;">
            <h3 style="margin-bottom: 10px;">{'Your Tongue Health Score' if lang == 'ENG' else '您的舌頭健康評分'}</h3>
            <div style="font-size: 64px; font-weight: bold; color: {score_color};">{score}</div>
            <div style="width: 100%; height: 20px; background-color: #f1f1f1; border-radius: 10px; margin: 15px 0;">
                <div style="width: {score}%; height: 100%; border-radius: 10px; background-color: {score_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show key findings
        st.markdown("### " + ("Key Findings" if lang == "ENG" else "主要發現"))
        
        # Extract key points
        result_text = st.session_state.tongue_analysis_result
        
        # Try to extract the first few lines of each section
        body_color_match = re.search(r'(?:Tongue Body Color|舌體顏色)[^\n]*\n([^\n#]+)', result_text, re.IGNORECASE)
        coating_match = re.search(r'(?:Tongue Coating|舌苔)[^\n]*\n([^\n#]+)', result_text, re.IGNORECASE)
        shape_match = re.search(r'(?:Tongue Shape|舌形)[^\n]*\n([^\n#]+)', result_text, re.IGNORECASE)
        
        # Display findings in a list with icons
        findings = []
        if body_color_match:
            findings.append(f"🟠 {'Body: ' if lang == 'ENG' else '舌體：'}{body_color_match.group(1).strip()}")
        if coating_match:
            findings.append(f"⚪ {'Coating: ' if lang == 'ENG' else '舌苔：'}{coating_match.group(1).strip()}")
        if shape_match:
            findings.append(f"📏 {'Shape: ' if lang == 'ENG' else '舌形：'}{shape_match.group(1).strip()}")
        
        # Display findings in a more attractive format
        for finding in findings:
            st.info(finding)
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                "📷 Retake Photo" if lang == "ENG" else "📷 重新拍照",
                type="secondary",
                use_container_width=True
            ):
                # Reset analysis data
                st.session_state.tongue_analysis_result = None
                st.session_state.tongue_analysis_score = None
                st.session_state.tongue_analysis_loading = False
                st.session_state.captured_image = None
                st.rerun()
        
        with col2:
            if st.button(
                "Continue to Weather & Season ➡️" if lang == "ENG" else "繼續到天氣與季節 ➡️",
                type="primary",
                use_container_width=True
            ):
                st.session_state.quick_start_step = 3
                st.rerun()
    
    # Show camera input if no analysis results yet
    else:
        # Camera interface
        camera_image = st.camera_input(
            "Take a photo of your tongue" if lang == "ENG" else "拍攝您的舌頭照片",
            help="Position your tongue clearly in the frame" if lang == "ENG" else "請將舌頭清晰地放在框架中",
            label_visibility="collapsed",
            key="camera_large_quick_start"
        )
        
        # When image is captured
        if camera_image is not None:
            # Store the image in session state
            st.session_state.captured_image = camera_image
            
            # Show analyze button
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.button(
                    "❌ Retake" if lang == "ENG" else "❌ 重拍",
                    on_click=lambda: st.session_state.update({"captured_image": None}),
                    use_container_width=True
                )
            
            with col2:
                if st.button(
                    "✅ Analyze this image" if lang == "ENG" else "✅ 分析此圖像",
                    type="primary",
                    use_container_width=True
                ):
                    # Set loading flag and trigger rerun
                    st.session_state.tongue_analysis_loading = True
                    st.rerun()
                    
        # Process the captured image
        if st.session_state.tongue_analysis_loading and 'captured_image' in st.session_state and st.session_state.captured_image is not None:
            with st.spinner("Analyzing tongue image... Please wait" if lang == "ENG" else "分析舌頭圖片中...請稍候"):
                try:
                    # Save the captured image to a temporary file
                    temp_image_path = "temp_tongue_image.jpg"
                    with open(temp_image_path, "wb") as f:
                        f.write(st.session_state.captured_image.getbuffer())
                    
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
                    
                    # Import required modules for Azure AI
                    from azure.ai.inference.models import (
                        SystemMessage,
                        UserMessage,
                        TextContentItem,
                        ImageContentItem,
                        ImageUrl,
                        ImageDetailLevel,
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
                        
                        # Extract score from the result using regex
                        score_pattern = r"## Health Score\s*(\d+)" if lang == "ENG" else r"## 健康評分\s*(\d+)"
                        score_match = re.search(score_pattern, result)
                        score = int(score_match.group(1)) if score_match else 70
                        
                        # Save results to session state
                        st.session_state.tongue_analysis_result = result
                        st.session_state.tongue_analysis_score = score
                        
                        # Mark this step as complete
                        st.session_state.tongue_data_complete = True
                        
                    except Exception as e:
                        st.error(f"Error analyzing image: {str(e)}")
                        st.session_state.tongue_analysis_result = f"Error: {str(e)}"
                    
                    # Clean up the temporary file
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
                        
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                
                # Turn off loading state
                st.session_state.tongue_analysis_loading = False
                st.rerun()
        
        # Navigation buttons (only shown when no analysis is happening)
        if not st.session_state.tongue_analysis_loading and camera_image is None:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(
                    "⬅️ " + ("Back: Personal Info" if lang == "ENG" else "返回：個人信息"), 
                    type="secondary",
                    use_container_width=True
                ):
                    st.session_state.quick_start_step = 1
                    st.rerun()
            
            with col2:
                if st.button(
                    "Skip this step ➡️" if lang == "ENG" else "跳過此步驟 ➡️", 
                    type="secondary",
                    use_container_width=True
                ):
                    st.session_state.quick_start_step = 3
                    st.rerun()

def show_quick_start_weather():
    """Step 3: Get weather and seasonal TCM advice"""
    lang = st.session_state.language
    
    st.markdown(f"""
    <h2 style='color: #5D5CDE; margin-bottom: 20px;'>{'Step 3: Weather & Seasonal Factors' if lang == 'ENG' else '步驟3：天氣與季節因素'}</h2>
    <p style='margin-bottom: 20px;'>{"TCM recommendations are influenced by seasonal changes and weather patterns. We'll retrieve the current traditional Chinese calendar information for you." if lang == 'ENG' else '中醫建議受季節變化和天氣模式的影響。我們將為您檢索當前的中國傳統曆法信息。'}</p>
    """, unsafe_allow_html=True)
    
    # Initialize session variables for weather data
    if 'lunar_info' not in st.session_state:
        st.session_state.lunar_info = None
    if 'advice' not in st.session_state:
        st.session_state.advice = None
    if 'weather_loading' not in st.session_state:
        st.session_state.weather_loading = True
    
    # Get date information
    date = datetime.now()
    formatted_date = date.strftime('%Y-%m-%d')
    
    # Main layout using columns
    col1, col2 = st.columns([1, 1])
    
    # Function to get current season
    def get_season_based_on_date():
        current_month = datetime.now().month
        
        if 3 <= current_month <= 5:
            return "Spring", "春季"
        elif 6 <= current_month <= 8:
            return "Summer", "夏季"
        elif 9 <= current_month <= 11:
            return "Autumn", "秋季"
        else:
            return "Winter", "冬季"
    
    season_eng, season_chi = get_season_based_on_date()
    
    with col1:
        # Gregorian calendar card
        day_of_week = date.strftime('%A')
        day_of_week_chinese = {
            'Monday': '星期一',
            'Tuesday': '星期二',
            'Wednesday': '星期三',
            'Thursday': '星期四',
            'Friday': '星期五',
            'Saturday': '星期六',
            'Sunday': '星期日'
        }.get(day_of_week, '')
        
        st.markdown(f"""
        <div style=" border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h3 style=" margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                📅 {'Gregorian Calendar' if lang == 'ENG' else '公曆'}
            </h3>
            <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-bottom: 15px;">
                <div style="font-size: 48px; font-weight: bold; color: #5D5CDE; margin-bottom: 5px;">{date.day}</div>
                <div style="font-size: 18px; color: #666;">{date.strftime('%B %Y') if lang == 'ENG' else f"{date.year}年{date.month}月"}</div>
                <div style="font-size: 16px; color: #888; margin-top: 5px;">{day_of_week if lang == 'ENG' else day_of_week_chinese}</div>
            </div>
            <div style=" padding: 10px; border-radius: 8px; margin-top: 15px;">
                <div style="font-size: 14px; color: #666; text-align: center;">
                    {'Current Season' if lang == 'ENG' else '當前季節'}: 
                    <span style="font-weight: bold; color: #5D5CDE;">{season_eng if lang == 'ENG' else season_chi}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Function to get Chinese zodiac
    def get_chinese_zodiac(lunar_year):
        # Chinese zodiac animals in order
        zodiac_animals = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
        zodiac_animals_chinese = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]
        
        # Calculate the zodiac animal (Chinese calendar starts from year 4)
        index = (lunar_year - 4) % 12
        return zodiac_animals[index], zodiac_animals_chinese[index]
    
    # Function to get zodiac emoji
    def get_zodiac_emoji(zodiac):
        """Return the emoji for the given zodiac animal."""
        zodiac_emojis = {
            'Rat': '🐭', 
            'Ox': '🐂', 
            'Tiger': '🐯', 
            'Rabbit': '🐰', 
            'Dragon': '🐲', 
            'Snake': '🐍', 
            'Horse': '🐴', 
            'Goat': '🐐', 
            'Monkey': '🐵', 
            'Rooster': '🐔', 
            'Dog': '🐶', 
            'Pig': '🐷'
        }
        return zodiac_emojis.get(zodiac, '🏮')
    
    # Load lunar calendar data
    if st.session_state.weather_loading:
        with col2:
            with st.spinner('Loading lunar calendar data...' if lang == 'ENG' else '正在加載農曆數據...'):
                try:
                    # Make API request to get lunar date
                    result = requests.get(f'https://data.weather.gov.hk/weatherAPI/opendata/lunardate.php?date={formatted_date}')
                    
                    if result.status_code == 200:
                        # Parse the JSON response
                        result_dict = result.json()
                        
                        if "LunarYear" in result_dict and "LunarDate" in result_dict:
                            lunar_year = result_dict["LunarYear"]
                            lunar_date = result_dict["LunarDate"]
                            
                            # Extract lunar day number for display
                            lunar_day_match = re.search(r'\d+', lunar_date)
                            lunar_day = lunar_day_match.group(0) if lunar_day_match else ""
                            
                            # Get zodiac info
                            zodiac_match = re.search(r'，(.+)$', lunar_year)
                            if zodiac_match:
                                zodiac_chi = zodiac_match.group(1)
                                zodiac_map = {
                                    "鼠": "Rat", "牛": "Ox", "虎": "Tiger", "兔": "Rabbit",
                                    "龍": "Dragon", "蛇": "Snake", "馬": "Horse", "羊": "Goat",
                                    "猴": "Monkey", "雞": "Rooster", "狗": "Dog", "豬": "Pig"
                                }
                                zodiac_eng = zodiac_map.get(zodiac_chi, "")
                            else:
                                # Try to extract numeric year
                                year_match = re.search(r'\d+', lunar_year)
                                if year_match:
                                    numeric_year = int(year_match.group(0))
                                    zodiac_eng, zodiac_chi = get_chinese_zodiac(numeric_year)
                                else:
                                    current_year = datetime.now().year
                                    zodiac_eng, zodiac_chi = get_chinese_zodiac(current_year)
                            
                            # Store in session state
                            st.session_state.lunar_info = {
                                "lunar_year": lunar_year,
                                "lunar_date": lunar_date,
                                "zodiac_eng": zodiac_eng,
                                "zodiac_chi": zodiac_chi,
                                "lunar_day": lunar_day
                            }
                            
                            # Generate TCM advice based on lunar date and season
                            # In the real implementation, this would call your AI model
                            # For quick start, we'll just provide some sample advice
                            if lang == "ENG":
                                tcm_advice = f"""What should I be mindful of today:
1. Today is in {season_eng} season, focus on balancing your {season_eng.lower()} energy
2. Pay attention to your digestive health as the {zodiac_eng} energy may affect your spleen
3. Stay hydrated with warm beverages throughout the day
4. Gentle stretching exercises will help maintain energy flow

Traditional Chinese Medicine prescription:
1. Chrysanthemum tea - Helps cool the liver and clear the eyes
2. Ginger with honey - Supports digestion and warms the body
3. Eight Treasure Tea - Balances yin and yang energies"""
                            else:
                                tcm_advice = f"""今天應該注意什麼：
1. 今天是{season_chi}，專注於平衡您的{season_chi}能量
2. 注意您的消化健康，因為{zodiac_chi}能量可能會影響您的脾臟
3. 全天飲用溫熱飲料保持水分
4. 輕柔的伸展運動將有助於維持能量流動

中藥處方：
1. 菊花茶 - 有助於冷卻肝臟並清晰眼睛
2. 薑加蜂蜜 - 支持消化並溫暖身體
3. 八寶茶 - 平衡陰陽能量"""
                            
                            st.session_state.advice = tcm_advice
                            st.session_state.weather_data_complete = True
                        else:
                            st.error("Failed to retrieve lunar date information." if lang == "ENG" else "無法獲取農曆日期信息。")
                    else:
                        st.error(f"API Error: {result.status_code}" if lang == "ENG" else f"API錯誤：{result.status_code}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                
                st.session_state.weather_loading = False
    
    # Display lunar calendar information
    with col2:
        if st.session_state.lunar_info:
            lunar_info = st.session_state.lunar_info
            
            # Lunar calendar card
            st.markdown(f"""
            <div style=" border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
                <h3 style=" margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                    🏮 {'Lunar Calendar' if lang == 'ENG' else '農曆'}
                </h3>
                <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-bottom: 15px;">
                    <div style="font-size: 48px; font-weight: bold; color: #E74C3C; margin-bottom: 5px;">{lunar_info['lunar_day']}</div>
                    <div style="font-size: 18px; color: #666;">{lunar_info['lunar_date'] if lang == 'ENG' else lunar_info['lunar_date']}</div>
                    <div style="font-size: 16px; color: #888; margin-top: 5px;">{lunar_info['lunar_year']} - {'Year of the ' + lunar_info['zodiac_eng'] if lang == 'ENG' else lunar_info['zodiac_chi'] + '年'}</div>
                </div>
                <div style=" padding: 10px; border-radius: 8px; margin-top: 15px; text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">
                        {get_zodiac_emoji(lunar_info['zodiac_eng'])}
                    </div>
                    <div style="font-size: 14px; color: #666;">
                        {'Chinese Zodiac' if lang == 'ENG' else '生肖'}: 
                        <span style="font-weight: bold; color: #E74C3C;">{lunar_info['zodiac_eng'] if lang == 'ENG' else lunar_info['zodiac_chi']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display placeholder if lunar info not yet loaded
            st.markdown(f"""
            <div style=" border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea; text-align: center;">
                <h3 style=" margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                    🏮 {'Lunar Calendar' if lang == 'ENG' else '農曆'}
                </h3>
                <div style="color: #666; padding: 40px 0;">
                    {'Loading lunar calendar information...' if lang == 'ENG' else '正在加載農曆信息...'}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # TCM Advice section
    st.markdown(f"""
        <h3 style=" margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
            🌿 {'Daily TCM Guidance' if lang == 'ENG' else '每日中醫指導'}
        </h3>
    """, unsafe_allow_html=True)
    
    # Display TCM advice
    if st.session_state.advice:
        advice = st.session_state.advice
        
        # Try to extract mindful and prescription sections
        mindful_pattern = r"(?:What should I be mindful of today:|今天應該注意什麼：)(.*?)(?:Traditional Chinese Medicine prescription:|中藥處方：)"
        prescription_pattern = r"(?:Traditional Chinese Medicine prescription:|中藥處方：)(.*)"
        
        mindful_match = re.search(mindful_pattern, advice, re.DOTALL)
        mindful = mindful_match.group(1).strip() if mindful_match else ""
        
        prescription_match = re.search(prescription_pattern, advice, re.DOTALL)
        prescription = prescription_match.group(1).strip() if prescription_match else ""
        
        # Display in a two-column layout
        if mindful and prescription:
            mindful_col, prescription_col = st.columns(2)
            
            with mindful_col:
                st.markdown(f"""
                <div style=" border-radius: 8px; padding: 15px; height: 100%;">
                    <h4 style="color: #5D5CDE; margin-bottom: 10px; font-size: 18px;">
                        {'Today\'s Mindfulness' if lang == 'ENG' else '今日注意事項'}
                    </h4>
                    <div style=" font-size: 14px;">
                        {mindful.replace('\n', '<br>')}
                    </div>
                </div><br>
                """, unsafe_allow_html=True)
            
            with prescription_col:
                st.markdown(f"""
                <div style=" border-radius: 8px; padding: 15px; height: 100%;">
                    <h4 style="color: #E74C3C; margin-bottom: 10px; font-size: 18px;">
                        {'Recommended Remedies' if lang == 'ENG' else '推薦的療法'}
                    </h4>
                    <div style=" font-size: 14px;">
                        {prescription.replace('\n', '<br>')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Just display the full advice
            st.markdown(f"""
            <div style="; border-radius: 8px; padding: 15px;">
                <div style=" font-size: 14px; white-space: pre-line;">
                    {advice}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                "⬅️ " + ("Back: Tongue Analysis" if lang == "ENG" else "返回：舌診分析"), 
                type="secondary",
                use_container_width=True
            ):
                st.session_state.quick_start_step = 2
                st.rerun()
        
        with col2:
            if st.button(
                "Next: Recommendations ➡️" if lang == "ENG" else "下一步：推薦 ➡️", 
                type="primary",
                use_container_width=True
            ):
                st.session_state.quick_start_step = 4
                st.rerun()
    else:
        # Display placeholder if advice not yet generated
        st.markdown("""
        <div style=" border-radius: 8px; padding: 15px; text-align: center;">
            <div style=" padding: 40px 0;">
                Generating personalized TCM advice...
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_quick_start_recommendation(client, model_name):
    """Step 4: Automatically generate comprehensive TCM recommendations"""
    lang = st.session_state.language
    
    st.markdown(f"""
    <h2 style='color: #5D5CDE; margin-bottom: 20px;'>{'Step 4: Your Personalized TCM Recommendations' if lang == 'ENG' else '步驟4：您的個性化中醫建議'}</h2>
    <p style='margin-bottom: 20px;'>{'Based on all the information collected, we are generating comprehensive TCM recommendations tailored to your specific needs.' if lang == 'ENG' else '根據收集的所有信息，我們正在生成針對您特定需求的全面中醫建議。'}</p>
    """, unsafe_allow_html=True)
    
    # Initialize session variables
    if 'recommendation' not in st.session_state:
        st.session_state.recommendation = None
    if 'recommendation_loading' not in st.session_state:
        st.session_state.recommendation_loading = True
    if 'additional_info' not in st.session_state:
        st.session_state.additional_info = ""
    
    # Get additional information input (optional - not forced)
    additional_info = st.text_area(
        "Any specific health concerns you'd like to add? (Optional)" if lang == "ENG" else "您想添加的任何特定健康問題？（可選）",
        value=st.session_state.additional_info,
        placeholder="For example: sleep quality, stress levels, digestive issues, pain, energy levels, etc." if lang == "ENG" else "例如：睡眠質量、壓力水平、消化問題、疼痛、能量水平等。",
        height=80
    )
    st.session_state.additional_info = additional_info
    
    # Generate recommendations automatically if not already done
    if st.session_state.recommendation_loading and not st.session_state.recommendation:
        with st.spinner("Analyzing your health data and generating recommendations..." if lang == "ENG" else "分析您的健康數據並生成建議..."):
            # Prepare user data for the prompt
            personal_info = {
                'name': st.session_state.get('name', 'Not provided'),
                'age': st.session_state.get('age', 'Not provided'),
                'gender': st.session_state.get('gender', 'Not provided'),
                'height': st.session_state.get('height', 'Not provided'),
                'weight': st.session_state.get('weight', 'Not provided'),
                'exercise_frequency': st.session_state.get('exercise_frequency', 'Not provided'),
                'health_history': st.session_state.get('health_history', 'Not provided')
            }
            
            weather_advice = st.session_state.get('advice', 'Not available')
            tongue_result = st.session_state.get('tongue_analysis_result', 'Not available')
            additional_info = st.session_state.additional_info
            
            # Create prompt based on language
            if lang == "ENG":
                user_prompt = f"""Please provide a comprehensive TCM health recommendation based on the following information:

### Weather and Seasonal Factors:
{weather_advice}

### Personal Information:
- Name: {personal_info['name']}
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
Provide a holistic, personalized health recommendation that considers all provided information."""

            else:
                user_prompt = f"""請根據以下信息提供全面的中醫健康建議：

### 天氣和季節因素：
{weather_advice}

### 個人信息：
- 姓名：{personal_info['name']}
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
4. 生活方式調整"""
                system_prompt = """您是一位經驗豐富的中醫師，擅長整合各種診斷方法。
請提供全面、個性化的健康建議，考慮所有提供的信息。"""
            
            try:
                # Generate the recommendation
                recommendation = advice_llm(system_prompt, user_prompt, model_type="openai")
                st.session_state.recommendation_lang = lang
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
            st.rerun()
    
    # Display the final recommendation with a better, more organized layout
    if st.session_state.recommendation:
        recommendation = st.session_state.recommendation
        
        # Format and display the recommendation
        st.markdown(recommendation)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Option to save/download the recommendation
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 " + ("Save Recommendations" if lang == "ENG" else "保存建議"), use_container_width=True):
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"tcm_recommendation_{timestamp}.txt"
                
                # Create a download link for the recommendation
                def get_download_link(text, filename):
                    b64 = base64.b64encode(text.encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Click here to download</a>'
                    return href
                
                download_link = get_download_link(recommendation, filename)
                st.markdown(f"{'Your recommendation is ready for download:' if lang == 'ENG' else '您的建議已準備好下載：'} {download_link}", unsafe_allow_html=True)
        
        with col2:
            # Button to complete the quick start process
            if st.button(
                "✨ " + ("Complete Quick Start" if lang == "ENG" else "完成快速入門"), 
                type="primary",
                use_container_width=True
            ):
                st.session_state.quick_start_step = 5
                st.rerun()
        
        # Option for going back or refreshing
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                "⬅️ " + ("Back: Weather & Season" if lang == "ENG" else "返回：天氣與季節"), 
                type="secondary",
                use_container_width=True
            ):
                st.session_state.quick_start_step = 3
                st.rerun()
        
        with col2:
            if st.button(
                "🔄 " + ("Refresh Recommendation" if lang == "ENG" else "刷新推薦"), 
                type="secondary",
                use_container_width=True
            ):
                st.session_state.recommendation = None
                st.session_state.recommendation_loading = True
                st.rerun()
    else:
        # Show animated loading state while generating recommendation
        st.markdown("""
        <div style="background-color: #f8f9fb; border-radius: 8px; padding: 30px; text-align: center; margin: 30px 0;">
            <div style="font-size: 18px; font-weight: bold; margin-bottom: 20px;">
                Generating Your Personalized TCM Recommendation
            </div>
            <div style="color: #666; margin: 20px 0;">
                Our AI is analyzing your data and creating a comprehensive TCM plan just for you...
            </div>
            <div style="width: 100%; height: 8px; background-color: #eee; border-radius: 4px; overflow: hidden;">
                <div style="width: 30%; height: 100%; background-color: #5D5CDE; border-radius: 4px; animation: pulse 1.5s infinite;"></div>
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
        
        # Navigation button to go back
        if st.button(
            "⬅️ " + ("Back: Weather & Season" if lang == "ENG" else "返回：天氣與季節"), 
            type="secondary",
            use_container_width=True
        ):
            st.session_state.quick_start_step = 3
            st.rerun()

def show_quick_start_complete():
    """Final step: Quick start completion with summary and next steps"""
    lang = st.session_state.language
    
    st.markdown(f"""
    <div style="text-align: center; padding: 30px 0;">
        <h1 style="color: #5D5CDE; margin-bottom: 30px;">{'✨ Quick Start Complete! ✨' if lang == 'ENG' else '✨ 快速入門完成！ ✨'}</h1>
        <p style="font-size: 18px; margin-bottom: 40px;">{'You\'ve successfully completed the quick start process and received your personalized TCM recommendations.' if lang == 'ENG' else '您已成功完成快速入門過程並收到個性化的中醫建議。'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary of collected data
    st.markdown(f"### {'Your Health Profile Summary' if lang == 'ENG' else '您的健康檔案摘要'}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Personal info summary
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h4 style="color: #5D5CDE; margin-bottom: 15px;">{'👤 Personal Information' if lang == 'ENG' else '👤 個人信息'}</h4>
            <ul style="list-style-type: none; padding: 0;">
                <li style="margin-bottom: 8px;"><strong>{'Name' if lang == 'ENG' else '姓名'}:</strong> {st.session_state.get('name', 'Not provided')}</li>
                <li style="margin-bottom: 8px;"><strong>{'Age' if lang == 'ENG' else '年齡'}:</strong> {st.session_state.get('age', 'Not provided')}</li>
                <li style="margin-bottom: 8px;"><strong>{'Gender' if lang == 'ENG' else '性別'}:</strong> {st.session_state.get('gender', 'Not provided')}</li>
                <li style="margin-bottom: 8px;"><strong>{'Height' if lang == 'ENG' else '身高'}:</strong> {st.session_state.get('height', 'Not provided')} cm</li>
                <li style="margin-bottom: 8px;"><strong>{'Weight' if lang == 'ENG' else '體重'}:</strong> {st.session_state.get('weight', 'Not provided')} kg</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Tongue analysis summary
        score = st.session_state.get('tongue_analysis_score', 'N/A')
        if score == 'N/A':
            score_color = "#666"
        else:
            try:
                score_num = float(score)
                score_color = "#2ecc71" if score_num >= 80 else "#f39c12" if score_num >= 60 else "#e74c3c"
            except (ValueError, TypeError):
                score_color = "#666"
            

        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h4 style="color: #5D5CDE; margin-bottom: 15px;">{'👅 Tongue Diagnosis' if lang == 'ENG' else '👅 舌診分析'}</h4>
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="font-size: 14px; margin-bottom: 5px;">{'Health Score' if lang == 'ENG' else '健康評分'}</div>
                <div style="font-size: 32px; font-weight: bold; color: {score_color};">{score}</div>
            </div>
            <div style="font-size: 14px; color: #666;">
                {'Tongue diagnosis complete. View detailed analysis in your recommendations.' if lang == 'ENG' else '舌診分析完成。在您的建議中查看詳細分析。'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Seasonal factors summary
        season_eng, season_chi = "Spring", "春季"  # You'd normally get this from your function
        current_month = datetime.now().month
        if 3 <= current_month <= 5:
            season_eng, season_chi = "Spring", "春季"
        elif 6 <= current_month <= 8:
            season_eng, season_chi = "Summer", "夏季"
        elif 9 <= current_month <= 11:
            season_eng, season_chi = "Autumn", "秋季"
        else:
            season_eng, season_chi = "Winter", "冬季"
        
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; padding-bottom: 98px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h4 style="color: #5D5CDE; margin-bottom: 15px;">{'🌤️ Seasonal Factors' if lang == 'ENG' else '🌤️ 季節因素'}</h4>
            <ul style="list-style-type: none; padding: 0;">
                <li style="margin-bottom: 8px;"><strong>{'Current Season' if lang == 'ENG' else '當前季節'}:</strong> {season_eng if lang == 'ENG' else season_chi}</li>
                <li style="margin-bottom: 8px;"><strong>{'Date' if lang == 'ENG' else '日期'}:</strong> {datetime.now().strftime('%Y-%m-%d')}</li>
            </ul>
            <div style="font-size: 14px; color: #666; margin-top: 15px;">
                {'Seasonal TCM guidance provided based on traditional Chinese calendar.' if lang == 'ENG' else '根據中國傳統曆法提供季節性中醫指導。'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recommendations summary
        has_recommendation = 'recommendation' in st.session_state and st.session_state.recommendation
        
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; margin-bottom: 20px; padding-bottom: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h4 style="color: #5D5CDE; margin-bottom: 15px;">{'💊 TCM Recommendations' if lang == 'ENG' else '💊 中醫建議'}</h4>
            <div style="text-align: center; margin: 15px 0;">
                <div style="font-size: 36px; color: {('#2ecc71' if has_recommendation else '#f39c12')};"> 
                    {'✓' if has_recommendation else '⚠️'}
                </div>
                <div style="font-size: 14px; margin-top: 10px; color: #666;">
                    {'Your personalized TCM recommendations are ready!' if has_recommendation else 'Recommendations not yet generated.'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Next steps section
    st.markdown(f"### {'What\'s Next?' if lang == 'ENG' else '接下來做什麼？'}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea; height: 100%;">
            <div style="font-size: 36px; margin-bottom: 15px;">🔍</div>
            <h4 style="color: #5D5CDE; margin-bottom: 10px;">{'Explore More Features' if lang == 'ENG' else '探索更多功能'}</h4>
            <p style="font-size: 14px;">{'Check out detailed tongue diagnosis, herb database, and more!' if lang == 'ENG' else '查看詳細舌診、藥材數據庫等！'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea; height: 100%;">
            <div style="font-size: 36px; margin-bottom: 15px;">📋</div>
            <h4 style="color: #5D5CDE; margin-bottom: 10px;">{'Track Your Progress' if lang == 'ENG' else '追踪您的進展'}</h4>
            <p style="font-size: 14px;">{'Update your profile regularly to see changes in your health status.' if lang == 'ENG' else '定期更新您的檔案，以查看健康狀況的變化。'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea; height: 100%;">
            <div style="font-size: 36px; margin-bottom: 15px;">💬</div>
            <h4 style="color: #5D5CDE; margin-bottom: 10px;">{'Ask AI Questions' if lang == 'ENG' else '向AI提問'}</h4>
            <p style="font-size: 14px;">{'Use the AI Chat feature to ask specific questions about TCM.' if lang == 'ENG' else '使用AI聊天功能詢問有關中醫的具體問題。'}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # Navigation buttons
    col1, col2 = st.columns(2)
    #add <br>
    
    with col1:
        if st.button(
            "🏠 " + ("Go to Home" if lang == "ENG" else "返回首頁"), 
            type="primary",
            use_container_width=True
        ):
            st.session_state.page = "main"
            st.rerun()
    
    with col2:
        if st.button(
            #set the button that reset the quick start step to 1
            "🔄 " + ("Start Over" if lang == "ENG" else "重新開始"),
            type="secondary",
            use_container_width=True
        ):
            st.session_state.page = "Quick Start"
            st.session_state.quick_start_step = 1
            st.session_state.personal_info_step = 1
            st.rerun()
