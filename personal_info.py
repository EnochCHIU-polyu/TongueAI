import streamlit as st

def show_personal_info():
    st.title("Personal Info")
    st.write("This is the content for Personal Info.")
    # Create a text input box for input the personal info like name, age, gender, height, weight, exercise frequency, etc.
    name = st.text_input("Name", value=st.session_state.get('name', None))
    age = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.get('age', None))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.get('gender', "Other")))
    height = st.number_input("Height (cm)", min_value=0, value=st.session_state.get('height', None))
    weight = st.number_input("Weight (kg)", min_value=0, value=st.session_state.get('weight', None))
    exercise_frequency = st.selectbox("Exercise Frequency", ["Never", "Rarely", "Sometimes", "Often", "Always"], index=["Never", "Rarely", "Sometimes", "Often", "Always"].index(st.session_state.get('exercise_frequency', "Never")))
    # Create a submit button to save the personal info
    if st.button("Submit"):
        st.session_state['name'] = name
        st.session_state['age'] = age
        st.session_state['gender'] = gender
        st.session_state['height'] = height
        st.session_state['weight'] = weight
        st.session_state['exercise_frequency'] = exercise_frequency