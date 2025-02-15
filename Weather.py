import streamlit as st
import requests
import json
import datetime
from llm_openai import advice_llm


def show_weather():
    st.title("Weather")
    # Get date from system
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    st.write("Today's date is: ", date)
    # Make a GET request to the weather API
    result = requests.get(f'https://data.weather.gov.hk/weatherAPI/opendata/lunardate.php?date={date}')
    
    if result.status_code == 200:
        # Save the JSON response to a file
        with open('weather.json', 'w') as f:
            output_json = json.dumps(result.json(), indent=4, sort_keys=True)
            f.write(output_json)
        
        # Parse the JSON response
        result_dict = result.json()
        
        # Display the weather information
        if "LunarYear" in result_dict and "LunarDate" in result_dict:
            st.write("Lunar Year:", result_dict["LunarYear"])
            st.write("Lunar Date:", result_dict["LunarDate"])
            
            # Save the weather information to session state
            if 'weather_info' not in st.session_state:
                st.session_state.weather_info = []
            
            weather_info = {
                "LunarYear": result_dict["LunarYear"],
                "LunarDate": result_dict["LunarDate"]
            }
            
            st.session_state.weather_info.append(weather_info)
            
            # Check the session state advice and display it if there is advice
            if 'advice' in st.session_state:
                st.write("Advice:", st.session_state.advice)
            else:
                user_prompt = f"根據傳統中醫的觀點，今天是{result_dict['LunarYear']}，{result_dict['LunarDate']}。請問今天應該注意什麼，應該吃什麼？"
                system_prompt = "Answer questions in traditional chinese, refer to the image for more context, and act like a traditional chinese medical expert."

                advice = advice_llm(system_prompt, user_prompt, model_type="openai")
                st.write("Advice:", advice)
                # Save the advice to session state
                st.session_state['advice'] = advice

        else:
            st.write("Failed to retrieve the expected weather information.")
    else:
        st.write("Failed to retrieve weather information.")

# Call the function to show weather and advice
show_weather()

