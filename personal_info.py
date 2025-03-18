import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

def calculate_bmi(weight, height):
    if weight <= 0 or height <= 0:
        return 0
    return round(weight / ((height/100) ** 2), 1)

def get_bmi_category(bmi):
    if bmi <= 0:
        return "N/A"
    elif bmi < 18.5:
        return "Underweight" if st.session_state.language == "ENG" else "體重過輕"
    elif bmi < 24:
        return "Normal" if st.session_state.language == "ENG" else "正常"
    elif bmi < 27:
        return "Overweight" if st.session_state.language == "ENG" else "過重"
    elif bmi < 30:
        return "Mild Obesity" if st.session_state.language == "ENG" else "輕度肥胖"
    elif bmi < 35:
        return "Moderate Obesity" if st.session_state.language == "ENG" else "中度肥胖"
    else:
        return "Severe Obesity" if st.session_state.language == "ENG" else "重度肥胖"

def get_bmi_color(bmi):
    if bmi <= 0:
        return "#888888"  # Gray for N/A
    elif bmi < 18.5:
        return "#3498db"  # Blue for Underweight
    elif bmi < 24:
        return "#2ecc71"  # Green for Normal
    elif bmi < 27:
        return "#f39c12"  # Orange for Overweight
    elif bmi < 30:
        return "#e67e22"  # Dark Orange for Mild Obesity
    elif bmi < 35:
        return "#e74c3c"  # Red for Moderate Obesity
    else:
        return "#c0392b"  # Dark Red for Severe Obesity

def create_profile_viz(name, age, gender, height, weight, exercise_frequency):
    fig, ax = plt.subplots(figsize=(6, 1.5))
    ax.axis('off')
    
    # Initialize data to display
    data = []
    if name:
        data.append(f"Name: {name}")
    if age > 0:
        data.append(f"Age: {age}")
    if gender != "---":
        data.append(f"Gender: {gender}")
    if height > 0:
        data.append(f"Height: {height} cm")
    if weight > 0:
        data.append(f"Weight: {weight} kg")
    
    # Display data as text
    if not data:
        ax.text(0.5, 0.5, "No profile data entered yet", ha='center', va='center', fontsize=12)
    else:
        for i, text in enumerate(data):
            ax.text(0.1, 0.9 - (i * 0.2), text, fontsize=11)
    
    # Set background color based on light/dark mode
    fig.patch.set_facecolor('none')
    ax.patch.set_facecolor('none')
    
    # Convert figure to image
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, bbox_inches='tight')
    buf.seek(0)
    return buf

def show_personal_info():
    lang = st.session_state.language
    
    # Initialize session state variables if not already present
    for key in ['name', 'age', 'gender', 'height', 'weight', 'exercise_frequency', 'health_history']:
        if key not in st.session_state:
            st.session_state[key] = '' if key in ['name', 'gender', 'exercise_frequency', 'health_history'] else 0
    
    if 'profile_history' not in st.session_state:
        st.session_state['profile_history'] = []
    
    # Page header
    st.markdown(f"<h1 style='color: #5D5CDE;'>{'Personal Health Profile' if lang == 'ENG' else '個人健康檔案'}</h1>", unsafe_allow_html=True)
    
    # Main layout using columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Profile information card
        st.markdown("""
            <h3 style="color: #333; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                🧑‍⚕️ {0}
            </h3>
        """.format(
            "Basic Information" if lang == "ENG" else "基本信息"
        ), unsafe_allow_html=True)
        
        # Form layout
        name = st.text_input(
            "Name" if lang == "ENG" else "姓名", 
            value=st.session_state.name,
            placeholder="Enter your name" if lang == "ENG" else "輸入您的姓名"
        )
        
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            age = st.number_input(
                "Age" if lang == "ENG" else "年齡", 
                min_value=0, 
                max_value=120, 
                value=st.session_state.age
            )
        
        with col1_2:
            gender_options = ["M", "F", "---"] 
            gender_index = gender_options.index(st.session_state.gender) if st.session_state.gender in gender_options else 2
            gender = st.selectbox(
                "Gender" if lang == "ENG" else "性別", 
                gender_options, 
                index=gender_index
            )
        
        col1_3, col1_4 = st.columns(2)
        with col1_3:
            height = st.number_input(
                "Height (cm)" if lang == "ENG" else "身高 (cm)", 
                min_value=0, 
                max_value=250, 
                value=st.session_state.height
            )
        
        with col1_4:
            weight = st.number_input(
                "Weight (kg)" if lang == "ENG" else "體重 (kg)", 
                min_value=0.0, 
                max_value=500.0, 
                value=float(st.session_state.weight),
                step=0.1
            )
        
        exercise_frequency_options = ["0", "1-2", "3-4", "5-6", ">7"]
        exercise_index = exercise_frequency_options.index(st.session_state.exercise_frequency) if st.session_state.exercise_frequency in exercise_frequency_options else 0
        exercise_frequency = st.selectbox(
            "Exercise Hours (Weekly)" if lang == "ENG" else "運動小時時數（每週）", 
            exercise_frequency_options, 
            index=exercise_index
        )
        
        # Health history textarea
        health_history = st.text_area(
            "Health Conditions & Medications" if lang == "ENG" else "健康狀況和藥物", 
            value=st.session_state.get('health_history', ''),
            placeholder="List any existing health conditions, allergies, or medications..." if lang == "ENG" else "列出任何現有的健康狀況，過敏或藥物...",
            height=100
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Submit button with improved styling
        col_submit, col_clear = st.columns([3, 1])
        with col_submit:
            submit_button = st.button(
                "💾 " + ("Save Profile" if lang == "ENG" else "保存檔案"), 
                type="primary",
                use_container_width=True
            )
        
        with col_clear:
            clear_button = st.button(
                "🗑️ " + ("Clear" if lang == "ENG" else "清除"), 
                type="secondary",
                use_container_width=True
            )
    
    with col2:
        # BMI Calculator Card
        bmi = calculate_bmi(weight, height)
        bmi_category = get_bmi_category(bmi)
        bmi_color = get_bmi_color(bmi)
        
        st.markdown(f"""
        <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; border: 1px solid #eaeaea;">
            <h3 style="color: #333; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                📊 {"BMI Calculator" if lang == "ENG" else "BMI 計算器"}
            </h3>
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="font-size: 48px; font-weight: bold; color: {bmi_color};">{bmi if bmi > 0 else '-'}</div>
                <div style="font-size: 18px; color: {bmi_color};">{bmi_category}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # BMI Scale
        if bmi > 0:
            # Calculate the position on the scale (0-100%)
            if bmi < 15:
                position = 0
            elif bmi > 40:
                position = 100
            else:
                position = min(100, max(0, (bmi - 15) * (100 / 25)))
            
            st.markdown(f"""
            <div style="width: 100%; height: 30px; background: linear-gradient(to right, #3498db, #2ecc71, #f39c12, #e74c3c); border-radius: 15px; position: relative; margin-bottom: 10px;">
                <div style="position: absolute; left: {position}%; top: -20px; transform: translateX(-50%);">
                    <div style="width: 2px; height: 15px; background-color: #333; margin: 0 auto;"></div>
                    <div style="width: 10px; height: 10px; background-color: #333; border-radius: 50%;"></div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 20px;">
                <div>15</div>
                <div>20</div>
                <div>25</div>
                <div>30</div>
                <div>35</div>
                <div>40</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
       
        
        # Profile visualization
        if height > 0 or weight > 0 or age > 0:
            profile_img = create_profile_viz(name, age, gender, height, weight, exercise_frequency)
        
        # Health tips based on BMI
        if bmi > 0:
            st.markdown(f"<h3 style='color: #333; margin-bottom: 10px; font-size: 18px;'>💡 {'Health Tips' if lang == 'ENG' else '健康提示'}</h3>", unsafe_allow_html=True)
            
            if bmi < 18.5:
                tip = "Consider increasing your calorie intake with nutrient-dense foods. Focus on protein-rich foods and strength training exercises." if lang == "ENG" else "考慮增加營養豐富食物的攝入量。專注於富含蛋白質的食物和力量訓練。"
            elif bmi < 24:
                tip = "Maintain your healthy habits! Regular exercise and a balanced diet will help you stay in this healthy range." if lang == "ENG" else "保持健康的習慣！定期運動和均衡飲食將幫助您保持在這個健康範圍內。"
            elif bmi < 27:
                tip = "Consider moderate calorie reduction and increased physical activity. Focus on whole foods and limiting processed foods." if lang == "ENG" else "考慮適度減少卡路里攝入並增加身體活動。專注於全食物，限制加工食品。"
            else:
                tip = "Consult with healthcare professionals for personalized advice. Consider a balanced diet with calorie control and regular exercise." if lang == "ENG" else "諮詢醫療專業人士獲取個性化建議。考慮卡路里控制的均衡飲食和定期運動。"
            
            st.markdown(f"<p style='margin-bottom: 10px;'>{tip}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # History section (collapsible)
    with st.expander(f"📋 {'Profile History' if lang == 'ENG' else '檔案歷史'}"):
        st.markdown(f"<p>{'View your profile changes over time' if lang == 'ENG' else '查看您的檔案隨時間的變化'}</p>", unsafe_allow_html=True)
        
        # Display history as a table if available
        if st.session_state.profile_history:
            history_df = pd.DataFrame(st.session_state.profile_history)
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No history available yet" if lang == "ENG" else "暫無歷史記錄")
    
    # Handle button actions
    if submit_button:
        # Save current profile data
        st.session_state.name = name
        st.session_state.age = age
        st.session_state.gender = gender
        st.session_state.height = height
        st.session_state.weight = weight
        st.session_state.exercise_frequency = exercise_frequency
        st.session_state.health_history = health_history
        
        # Add to history with timestamp
        history_entry = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Height (cm)": height,
            "Weight (kg)": weight,
            "BMI": bmi,
            "Exercise (hrs/week)": exercise_frequency
        }
        st.session_state.profile_history.append(history_entry)
        
        # Show success message
        st.success("Profile saved successfully!" if lang == "ENG" else "檔案保存成功！")
        
    if clear_button:
        # Reset form fields but keep history
        st.session_state.name = ""
        st.session_state.age = 0
        st.session_state.gender = "---"
        st.session_state.height = 0
        st.session_state.weight = 0
        st.session_state.exercise_frequency = "0"
        st.session_state.health_history = ""
        st.rerun()

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
            
            h3[style*="color: #333"] {
                color: #e0e0e0 !important;
                border-bottom-color: #444 !important;
            }
            
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            .stSelectbox, .stTextArea textarea {
                background-color: #3d3d3d !important;
                color: #e0e0e0 !important;
            }
            
            p, div {
                color: #e0e0e0 !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)