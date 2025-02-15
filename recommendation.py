import streamlit as st
import requests
import json
from llm_openai import advice_llm

def llm_recommendation():
    user_prompt = (
        f"{st.session_state.get('advice', None)}，"
        f"以下是我的個人資料："
        f"年齡：{st.session_state.get('age', None)}，"
        f"性別：{st.session_state.get('gender', None)}，"
        f"身高：{st.session_state.get('height', None)}厘米，"
        f"體重：{st.session_state.get('weight', None)}公斤，"
        f"運動頻率：{st.session_state.get('exercise_frequency', None)}，"
        f"舌診結果：{st.session_state.get('result', None)}。"
        f"for additional:{st.session_state.get('additional_info', None)}"
    )
    system_prompt = "Answer questions in traditional chinese, and act like a traditional chinese medical expert. For detail please give a diagnosis  with at least 3 type Chinese medicine prescription based on the information with detail(Processing methon), consider to the weather, personal info and the tongue_detect_result which is important."

    recommendation = advice_llm(system_prompt, user_prompt, model_type="openai")
    #st.write("Advice:", recommendation)

    # Save the advice to session state
    st.session_state['recommendation'] = recommendation
    return recommendation

def show_recommendation():
    llm_recommendation()
    st.title("Recommendation")
    # let user input additional input for more detail
    st.write("Please provide additional information for more detail.")
    user_input = st.text_area("Additional Information", value=st.session_state.get('additional_info', None))
    if user_input:
        st.session_state['additional_info'] = user_input
    #button to reset the advice
    if st.button("Submit"):
        llm_recommendation()
    st.write("Advice:", st.session_state.get('recommendation', None))
    #getting all session state data from the previous pages and displaying it
    st.write("### Personal Info")
    if 'name' in st.session_state:
        st.write("Name:", st.session_state['name'])
    else:
        st.write("Name:", "No name provided")
    if 'age' in st.session_state:
        st.write("Age:", st.session_state['age'])
    else:
        st.write("Age:", "No age provided")
    if 'gender' in st.session_state:
        st.write("Gender:", st.session_state['gender'])
    else:
        st.write("Gender:", "No gender provided")

    if 'height' in st.session_state:
        st.write("Height:", st.session_state['height'])
    else:
        st.write("Height:", "No height provided")

    if 'weight' in st.session_state:
        st.write("Weight:", st.session_state['weight'])
    else:
        st.write("Weight:", "No weight provided")

    if 'exercise_frequency' in st.session_state:
        st.write("Exercise frequency:", st.session_state['exercise_frequency'])
    else:
        st.write("Exercise frequency:", "No exercise frequency provided")

    st.write("### Tongue Detect Result")
    if 'result' in st.session_state:
        st.write("Tongue Detect Result:", st.session_state.result)
    else:
        st.write("Tongue Detect Result:", "No result provided")

    st.write("### Weather Info")
    if 'advice' in st.session_state:
        st.write("Advice:", st.session_state.advice)
    else:
        st.write("Advice:", "No advice provided")

