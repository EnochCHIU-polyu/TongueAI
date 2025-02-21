import streamlit as st

def show_personal_info():
    st.title("Personal Info" if st.session_state.language == "ENG" else "個人信息")
    st.write("This is the content for Personal Info." if st.session_state.language == "ENG" else "這是個人信息的內容。")
    
    # Create a text input box for input the personal info like name, age, gender, height, weight, exercise frequency, etc.
    name = st.text_input("Name" if st.session_state.language == "ENG" else "姓名", value=st.session_state.get('name', ''))
    age = st.number_input("Age" if st.session_state.language == "ENG" else "年齡", min_value=0, max_value=120, value=st.session_state.get('age', 0))
    
    gender_options = ["M", "F", "---"] if st.session_state.language == "ENG" else ["M", "F", "---"] 
    gender_default = st.session_state.get('gender', "---" if st.session_state.language == "ENG" else "---")
    gender = st.selectbox("Gender" if st.session_state.language == "ENG" else "性別", gender_options, index=gender_options.index(gender_default))
    
    height = st.number_input("Height (cm)" if st.session_state.language == "ENG" else "身高 (cm)", min_value=0, value=st.session_state.get('height', 0))
    weight = st.number_input("Weight (kg)" if st.session_state.language == "ENG" else "體重 (kg)", min_value=0, value=st.session_state.get('weight', 0))
    
    exercise_frequency_options = ["0", "1-2", "3-4", "5-6", ">7"] 
    exercise_frequency_default = st.session_state.get('exercise_frequency', "0")
    exercise_frequency = st.selectbox("Exercise Hours (Weekly)" if st.session_state.language == "ENG" else "運動小時時數（每週）", exercise_frequency_options, index=exercise_frequency_options.index(exercise_frequency_default))
    
    # Create a submit button to save the personal info
    if st.button("Submit" if st.session_state.language == "ENG" else "提交"):
        st.session_state['name'] = name
        st.session_state['age'] = age
        st.session_state['gender'] = gender
        st.session_state['height'] = height
        st.session_state['weight'] = weight
        st.session_state['exercise_frequency'] = exercise_frequency
        st.write("Personal info saved." if st.session_state.language == "ENG" else "個人信息已保存。")