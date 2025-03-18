import streamlit as st
import requests
import json
import datetime
import time
from llm_openai import advice_llm
import pandas as pd
import re
import base64

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

def get_chinese_zodiac(lunar_year):
    # Chinese zodiac animals in order
    zodiac_animals = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
    zodiac_animals_chinese = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]
    
    # Calculate the zodiac animal (Chinese calendar starts from year 4)
    index = (lunar_year - 4) % 12
    return zodiac_animals[index], zodiac_animals_chinese[index]

def get_season_based_on_date():
    current_month = datetime.datetime.now().month
    
    if 3 <= current_month <= 5:
        return "Spring", "春季"
    elif 6 <= current_month <= 8:
        return "Summer", "夏季"
    elif 9 <= current_month <= 11:
        return "Autumn", "秋季"
    else:
        return "Winter", "冬季"

def extract_advice_sections(advice_text):
    """Extract sections from the advice text."""
    mindful_pattern = r"(?:What should I be mindful of today:|今天應該注意什麼：)(.*?)(?:Traditional Chinese Medicine prescription:|中藥處方：)"
    prescription_pattern = r"(?:Traditional Chinese Medicine prescription:|中藥處方：)(.*)"
    
    # Find what to be mindful of
    mindful_match = re.search(mindful_pattern, advice_text, re.DOTALL)
    mindful = mindful_match.group(1).strip() if mindful_match else ""
    
    # Find TCM prescription
    prescription_match = re.search(prescription_pattern, advice_text, re.DOTALL)
    prescription = prescription_match.group(1).strip() if prescription_match else ""
    
    if not mindful and not prescription:
        # If patterns don't match, just split the text in half
        parts = advice_text.split("\n\n", 1)
        if len(parts) > 1:
            mindful = parts[0]
            prescription = parts[1]
        else:
            mindful = advice_text
            prescription = ""
    
    return mindful, prescription

def show_weather():
    # Initialize session state variables
    if 'weather_info' not in st.session_state:
        st.session_state.weather_info = []
    if 'advice' not in st.session_state:
        st.session_state.advice = None
    if 'advice_language' not in st.session_state:
        st.session_state.advice_language = st.session_state.language if 'language' in st.session_state else "ENG"
    if 'language' not in st.session_state:
        st.session_state.language = "ENG"
    if 'weather_loading' not in st.session_state:
        st.session_state.weather_loading = False
        
    lang = st.session_state.language
    
    # Page header
    st.markdown(f"<h1 style='color: #5D5CDE;'>{'Traditional Chinese Calendar' if lang == 'ENG' else '中國傳統曆法'}</h1>", unsafe_allow_html=True)
    
    # Get date and season information
    date = datetime.datetime.now()
    formatted_date = date.strftime('%Y-%m-%d')
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
    
    season_eng, season_chi = get_season_based_on_date()
    
    # Main layout using columns
    date_col, lunar_col = st.columns([1, 1])
    
    with date_col:
        # Gregorian calendar card
        st.markdown(f"""
        <div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h3 style="color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                📅 {'Gregorian Calendar' if lang == 'ENG' else '公曆'}
            </h3>
            <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-bottom: 15px;">
                <div style="font-size: 48px; font-weight: bold; color: #5D5CDE; margin-bottom: 5px;">{date.day}</div>
                <div style="font-size: 18px; color: #666;">{date.strftime('%B %Y') if lang == 'ENG' else f"{date.year}年{date.month}月"}</div>
                <div style="font-size: 16px; color: #888; margin-top: 5px;">{day_of_week if lang == 'ENG' else day_of_week_chinese}</div>
            </div>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin-top: 15px;">
                <div style="font-size: 14px; color: #666; text-align: center;">
                    {'Current Season' if lang == 'ENG' else '當前季節'}: 
                    <span style="font-weight: bold; color: #5D5CDE;">{season_eng if lang == 'ENG' else season_chi}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Make API request to get lunar date information
    try:
        if not st.session_state.weather_loading:
            with lunar_col:
                with st.spinner('Loading lunar calendar data...' if lang == 'ENG' else '正在加載農曆數據...'):
                    st.session_state.weather_loading = True
                    
                    # Make a GET request to the weather API
                    result = requests.get(f'https://data.weather.gov.hk/weatherAPI/opendata/lunardate.php?date={formatted_date}')
                    
                    if result.status_code == 200:
                        # Save the JSON response to a file
                        with open('weather.json', 'w') as f:
                            output_json = json.dumps(result.json(), indent=4, sort_keys=True)
                            f.write(output_json)
                        
                        # Parse the JSON response
                        result_dict = result.json()
                        
                        if "LunarYear" in result_dict and "LunarDate" in result_dict:
                            lunar_year = result_dict["LunarYear"]
                            lunar_date = result_dict["LunarDate"]
                            
                            # Extract lunar day number for display
                            lunar_day_match = re.search(r'\d+', lunar_date)
                            lunar_day = lunar_day_match.group(0) if lunar_day_match else ""
                            
                            # Extract zodiac information directly from the response if possible
                            # For traditional Chinese lunar year format like "乙巳年，蛇"
                            zodiac_chi = ""
                            zodiac_eng = ""
                            
                            # Check if lunar_year contains zodiac info directly
                            zodiac_match = re.search(r'，(.+)$', lunar_year)
                            if zodiac_match:
                                # If format is like "乙巳年，蛇" extract the animal name
                                zodiac_chi = zodiac_match.group(1)
                                # Map Chinese zodiac to English
                                zodiac_map = {
                                    "鼠": "Rat", "牛": "Ox", "虎": "Tiger", "兔": "Rabbit",
                                    "龍": "Dragon", "蛇": "Snake", "馬": "Horse", "羊": "Goat",
                                    "猴": "Monkey", "雞": "Rooster", "狗": "Dog", "豬": "Pig"
                                }
                                zodiac_eng = zodiac_map.get(zodiac_chi, "")
                            else:
                                # Try to extract a numeric year and calculate
                                try:
                                    # Try to extract numeric part if it exists
                                    year_match = re.search(r'\d+', lunar_year)
                                    if year_match:
                                        numeric_year = int(year_match.group(0))
                                        zodiac_eng, zodiac_chi = get_chinese_zodiac(numeric_year)
                                    else:
                                        # Fallback to current year if no numeric part
                                        current_year = datetime.datetime.now().year
                                        zodiac_eng, zodiac_chi = get_chinese_zodiac(current_year)
                                except Exception:
                                    # Fallback to current year if conversion fails
                                    current_year = datetime.datetime.now().year
                                    zodiac_eng, zodiac_chi = get_chinese_zodiac(current_year)
                            
                            # Store in session state
                            st.session_state.lunar_info = {
                                "lunar_year": lunar_year,
                                "lunar_date": lunar_date,
                                "zodiac_eng": zodiac_eng,
                                "zodiac_chi": zodiac_chi,
                                "lunar_day": lunar_day
                            }
                            
                            # Save to weather info list
                            weather_info = {
                                "LunarYear": lunar_year,
                                "LunarDate": lunar_date
                            }
                            st.session_state.weather_info.append(weather_info)
                        else:
                            st.error("Failed to retrieve lunar date information." if lang == "ENG" else "無法獲取農曆日期信息。")
                    else:
                        st.error(f"API Error: {result.status_code}" if lang == "ENG" else f"API錯誤：{result.status_code}")
                        
                    st.session_state.weather_loading = False
        
        # Display lunar calendar information if available
        with lunar_col:
            if hasattr(st.session_state, 'lunar_info'):
                lunar_info = st.session_state.lunar_info
                
                # Lunar calendar card
                st.markdown(f"""
                <div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
                    <h3 style="color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                        🏮 {'Lunar Calendar' if lang == 'ENG' else '農曆'}
                    </h3>
                    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-bottom: 15px;">
                        <div style="font-size: 48px; font-weight: bold; color: #E74C3C; margin-bottom: 5px;">{lunar_info['lunar_day']}</div>
                        <div style="font-size: 18px; color: #666;">{lunar_info['lunar_date'] if lang == 'ENG' else lunar_info['lunar_date']}</div>
                        <div style="font-size: 16px; color: #888; margin-top: 5px;">{lunar_info['lunar_year']} - {'Year of the ' + lunar_info['zodiac_eng'] if lang == 'ENG' else lunar_info['zodiac_chi'] + '年'}</div>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin-top: 15px; text-align: center;">
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
                <div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea; text-align: center;">
                    <h3 style="color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                        🏮 {'Lunar Calendar' if lang == 'ENG' else '農曆'}
                    </h3>
                    <div style="color: #666; padding: 40px 0;">
                        {'Loading lunar calendar information...' if lang == 'ENG' else '正在加載農曆信息...'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # TCM Advice section
        st.markdown(f"""
            <h3 style="color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                🌿 {'Daily TCM Guidance' if lang == 'ENG' else '每日中醫指導'}
            </h3>
        """, unsafe_allow_html=True)
        
        # Check if we need to generate new advice
        generate_new_advice = False
        
        if 'advice' not in st.session_state or st.session_state.advice is None:
            generate_new_advice = True
        elif st.session_state.advice_language != lang:
            generate_new_advice = True
        elif hasattr(st.session_state, 'lunar_info') and st.session_state.lunar_info and 'last_advice_date' in st.session_state:
            # Check if the advice is from today
            if st.session_state.last_advice_date != formatted_date:
                generate_new_advice = True
        else:
            generate_new_advice = True
        
        # Generate advice if needed
        if generate_new_advice and hasattr(st.session_state, 'lunar_info') and st.session_state.lunar_info:
            lunar_info = st.session_state.lunar_info
            
            with st.spinner('Generating TCM advice...' if lang == 'ENG' else '生成中醫建議...'):
                if lang == "ENG":
                    user_prompt = f"According to traditional Chinese medicine, today is {lunar_info['lunar_year']}, {lunar_info['lunar_date']}, which is in {season_eng}. Provide advice in the following format:\n\nWhat should I be mindful of today: [provide 3-4 seasonal health tips based on TCM principles for this specific lunar date and season]\n\nTraditional Chinese Medicine prescription: [suggest 2-3 specific herbal formulas or teas that would be beneficial today, with brief explanations of their benefits]"
                    system_prompt = "You are a highly knowledgeable Traditional Chinese Medicine doctor with deep understanding of seasonal health practices. Provide practical, concise advice that connects lunar calendar dates with appropriate TCM recommendations."
                else:
                    user_prompt = f"根據傳統中醫的觀點，今天是{lunar_info['lunar_year']}，{lunar_info['lunar_date']}，現在是{season_chi}。請按以下格式提供建議：\n\n今天應該注意什麼：[根據中醫原則，提供3-4個針對這個特定農曆日期和季節的季節性健康提示]\n\n中藥處方：[建議2-3種對今天有益的特定草藥配方或茶，並簡要說明其益處]"
                    system_prompt = "您是一位知識淵博的中醫醫生，對季節性健康實踐有深入的了解。提供將農曆日期與適當的中醫建議相連接的實用、簡潔的建議。"

                advice = advice_llm(system_prompt, user_prompt, model_type="openai")
                
                # Save the advice to session state
                st.session_state.advice = advice
                st.session_state.advice_language = lang
                st.session_state.last_advice_date = formatted_date
        
        # Display TCM advice if available
        if 'advice' in st.session_state and st.session_state.advice:
            advice = st.session_state.advice
            
            # Try to extract mindful and prescription sections
            mindful, prescription = extract_advice_sections(advice)
            
            # Display in a nicer format with columns
            if mindful and prescription:
                mindful_col, prescription_col = st.columns(2)
                
                with mindful_col:
                    st.markdown(f"""
                    <div style="background-color: #f8f9fb; border-radius: 8px; padding: 15px; height: 100%;">
                        <h4 style="color: #5D5CDE; margin-bottom: 10px; font-size: 18px;">
                            {'Today\'s Mindfulness' if lang == 'ENG' else '今日注意事項'}
                        </h4>
                        <div style="color: #333; font-size: 14px;">
                            {mindful.replace('\n', '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with prescription_col:
                    st.markdown(f"""
                    <div style="background-color: #f8f9fb; border-radius: 8px; padding: 15px; height: 100%;">
                        <h4 style="color: #E74C3C; margin-bottom: 10px; font-size: 18px;">
                            {'Recommended Remedies' if lang == 'ENG' else '推薦的療法'}
                        </h4>
                        <div style="color: #333; font-size: 14px;">
                            {prescription.replace('\n', '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Just display the full advice
                st.markdown(f"""
                <div style="background-color: #f8f9fb; border-radius: 8px; padding: 15px;">
                    <div style="color: #333; font-size: 14px; white-space: pre-line;">
                        {advice}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Share or refresh button
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("📤 " + ("Share This Advice" if lang == "ENG" else "分享這個建議"), use_container_width=True):
                    timestamp = datetime.datetime.now().strftime("%Y%m%d")
                    advice_text = f"TCM Advice for {formatted_date}:\n\n{advice}"
                    
                    # Create a download link for the advice
                    def get_download_link(text, filename):
                        b64 = base64.b64encode(text.encode()).decode()
                        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Click here to download</a>'
                        return href
                    
                    filename = f"tcm_advice_{timestamp}.txt"
                    download_link = get_download_link(advice_text, filename)
                    st.markdown(f"{'Your advice is ready for download:' if lang == 'ENG' else '您的建議已準備好下載：'} {download_link}", unsafe_allow_html=True)
            
            with col2:
                if st.button("🔄 " + ("Refresh" if lang == "ENG" else "刷新"), use_container_width=True):
                    st.session_state.advice = None
                    st.experimental_rerun()
        else:
            # Display placeholder if advice not yet generated
            st.markdown("""
            <div style="background-color: #f8f9fb; border-radius: 8px; padding: 15px; text-align: center;">
                <div style="color: #666; padding: 40px 0;">
                    Generating personalized TCM advice...
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Health tips based on season
        season_tips = {
            "Spring": {
                "ENG": [
                    "Rise earlier with the sun, as yang energy begins to grow",
                    "Engage in gentle stretching to promote liver qi flow",
                    "Eat fresh greens and sprouts that support liver function",
                    "Practice deep breathing to cleanse and rejuvenate"
                ],
                "中文": [
                    "隨著陽氣開始生長，早起與太陽一同起床",
                    "進行輕柔的伸展運動以促進肝氣流動",
                    "食用支持肝功能的新鮮蔬菜和芽菜",
                    "練習深呼吸以淨化和恢復活力"
                ]
            },
            "Summer": {
                "ENG": [
                    "Stay hydrated with cooling drinks like chrysanthemum tea",
                    "Reduce intensity of activities during peak heat",
                    "Eat cooling foods like watermelon, cucumber, and mint",
                    "Protect heart energy by avoiding excessive stress"
                ],
                "中文": [
                    "飲用菊花茶等清涼飲品保持水分",
                    "在高溫時段減少活動強度",
                    "食用西瓜、黃瓜和薄荷等清涼食物",
                    "避免過度壓力以保護心臟能量"
                ]
            },
            "Autumn": {
                "ENG": [
                    "Focus on lung health through gentle breathing exercises",
                    "Moisturize the body inside and out as dryness increases",
                    "Eat white foods like pears and rice to support lung qi",
                    "Begin to conserve energy as yin starts to grow"
                ],
                "中文": [
                    "通過輕柔的呼吸練習專注於肺部健康",
                    "隨著乾燥增加，保持身體內外的滋潤",
                    "食用梨和米等白色食物以支持肺氣",
                    "隨著陰氣開始生長，開始保存能量"
                ]
            },
            "Winter": {
                "ENG": [
                    "Preserve kidney energy by getting adequate rest",
                    "Keep lower back and feet warm to protect kidney yang",
                    "Eat warming foods like soups, stews, and root vegetables",
                    "Practice meditation to nurture inner stillness"
                ],
                "中文": [
                    "通過充分休息保存腎臟能量",
                    "保持下背部和腳部溫暖以保護腎陽",
                    "食用湯、燉菜和根莖類蔬菜等溫熱食物",
                    "練習冥想培養內在平靜"
                ]
            }
        }
        
        current_season = season_eng
        tips = season_tips[current_season]["ENG" if lang == "ENG" else "中文"]
        
        # Seasonal health tips
        st.markdown(f"""
        <div style="background-color: white; border-radius: 10px; padding: 20px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #eaeaea;">
            <h3 style="color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                🍃 {'Seasonal Health Tips' if lang == 'ENG' else '季節健康提示'}
            </h3>
            <div style="color: #666; margin-bottom: 20px; font-size: 16px;">
                {'According to TCM, each season requires different approaches to maintain optimal health and balance.' if lang == 'ENG' else '根據中醫理論，每個季節都需要不同的方法來保持最佳健康和平衡。'}
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
        """, unsafe_allow_html=True)
        
        for i, tip in enumerate(tips):
            icon = ["🌱", "🍵", "🥗", "🧘‍♀️"][i % 4]
            st.markdown(f"""
            <div style="background-color: #f8f9fb; border-radius: 8px; padding: 15px;">
                <div style="font-size: 24px; margin-bottom: 10px;">{icon}</div>
                <div style="color: #333; font-size: 14px;">{tip}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
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
            
            h3[style*="color: #333"], h4[style*="color: #5D5CDE"], h4[style*="color: #E74C3C"] {
                color: #e0e0e0 !important;
                border-bottom-color: #444 !important;
            }
            
            div[style*="color: #666"], div[style*="color: #333"], div[style*="color: #888"] {
                color: #e0e0e0 !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)