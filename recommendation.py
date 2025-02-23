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
    if st.session_state.language == "ENG":
        system_prompt = "Answer questions in English, and act like a traditional Chinese medical expert. For detail please give a diagnosis  with at least 3 type Chinese medicine prescription based on the information with detail(Processing methon), consider to the weather, personal info and the tongue_detect_result which is important."
    else:
        system_prompt = "Answer questions in traditional chinese, and act like a traditional chinese medical expert. For detail please give a diagnosis  with at least 3 type Chinese medicine prescription based on the information with detail(Processing methon), consider to the weather, personal info and the tongue_detect_result which is important."

    recommendation = advice_llm(system_prompt, user_prompt, model_type="openai")
    #st.write("Advice:", recommendation)

    # Save the advice to session state
    st.session_state['recommendation'] = recommendation
    return recommendation

def show_recommendation():
    llm_recommendation()
    st.title("Recommendation") if st.session_state.language == "ENG" else st.title("推薦")
    # let user input additional input for more detail
    st.write("Please provide additional information for more detail.") if st.session_state.language == "ENG" else st.write("請提供更多的信息以獲得更多的建議。")
    user_input = st.text_area("Additional Information", value=st.session_state.get('additional_info', None)) if st.session_state.language == "ENG" else st.text_area("更多信息", value=st.session_state.get('additional_info', None))
    if user_input:
        st.session_state['additional_info'] = user_input
    #button to reset the advice
    if st.button("Submit") if st.session_state.language == "ENG" else st.button("提交"):
        llm_recommendation()
    st.write(st.session_state.get('recommendation', None))
    #getting all session state data from the previous pages and displaying it
    st.write("### Personal Info") if st.session_state.language == "ENG" else st.write("### 個人信息")
    if 'name' in st.session_state:
        st.write("Name:", st.session_state['name']) if st.session_state.language == "ENG" else st.write("姓名:", st.session_state['name'])
    else:
        st.write("Name:", "No name provided") if st.session_state.language == "ENG" else st.write("姓名:", "沒有提供姓名")
    if 'age' in st.session_state:
        st.write("Age:", st.session_state['age']) if st.session_state.language == "ENG" else st.write("年齡:", st.session_state['age'])
    else:
        st.write("Age:", "No age provided") if st.session_state.language == "ENG" else st.write("年齡:", "沒有提供年齡")
    if 'gender' in st.session_state:
        st.write("Gender:", st.session_state['gender']) if st.session_state.language == "ENG" else st.write("性別:", st.session_state['gender'])
    else:
        st.write("Gender:", "No gender provided") if st.session_state.language == "ENG" else st.write("性別:", "沒有提供性別")

    if 'height' in st.session_state:
        st.write("Height:", st.session_state['height']) if st.session_state.language == "ENG" else st.write("身高:", st.session_state['height'])
    else:
        st.write("Height:", "No height provided") if st.session_state.language == "ENG" else st.write("身高:", "沒有提供身高")

    if 'weight' in st.session_state:
        st.write("Weight:", st.session_state['weight']) if st.session_state.language == "ENG" else st.write("體重:", st.session_state['weight'])
    else:
        st.write("Weight:", "No weight provided") if st.session_state.language == "ENG" else st.write("體重:", "沒有提供體重")

    if 'exercise_frequency' in st.session_state:
        st.write("Exercise frequency:", st.session_state['exercise_frequency']) if st.session_state.language == "ENG" else st.write("運動頻率:", st.session_state['exercise_frequency'])
    else:
        st.write("Exercise frequency:", "No exercise frequency provided") if st.session_state.language == "ENG" else st.write("運動頻率:", "沒有提供運動頻率")

    st.write("### Tongue Detect Result") if st.session_state.language == "ENG" else st.write("### 舌診結果")
    if 'result' in st.session_state:
        st.write("Tongue Detect Result:", st.session_state.result)
    else:
        st.write("Tongue Detect Result:", "No result provided")

    st.write("### Weather Info") if st.session_state.language == "ENG" else st.write("### 天氣信息")
    if 'advice' in st.session_state:
        st.write("Advice:", st.session_state.advice)
    else:
        st.write("Advice:", "No advice provided")

