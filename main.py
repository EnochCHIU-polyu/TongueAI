# In main.py
import os
import toml
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from personal_info import show_personal_info
from tongue_detect import show_tongue_detect
from Weather import show_weather
from recommendation import show_recommendation
from herb_check import show_herb
from herb_inventory import show_herb_inventory
import streamlit as st
import base64
from quick_start import show_quick_start  # Import the quick start module

# Load API key from secrets manager
secrets = st.secrets

token = secrets['OPENAI']['OPENAI_API_KEY']
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

# Set page configuration
st.set_page_config(
    page_title="AI TCM Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize additional session state variables for quick start
if 'quick_start_step' not in st.session_state:
    st.session_state.quick_start_step = 1
if 'personal_data_complete' not in st.session_state:
    st.session_state.personal_data_complete = False
if 'tongue_data_complete' not in st.session_state:
    st.session_state.tongue_data_complete = False
if 'weather_data_complete' not in st.session_state:
    st.session_state.weather_data_complete = False
if 'final_recommendation' not in st.session_state:
    st.session_state.final_recommendation = None

# Custom CSS for better UI
def local_css():
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background-color: #f8f9fa;
            padding: 2rem;
        }
        
        /* Feature card */
        .feature-card {
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: 1px solid #eaeaea;
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 10px;
            color: #5D5CDE;
        }
        
        .feature-title {
            font-weight: bold;
            font-size: 1.2rem;
            margin-bottom: 10px;
        }
        
        .feature-description {
            font-size: 0.9rem;
        }
        
        /* Language selector */
        .language-btn {
            padding: 5px 15px;
            border-radius: 20px;
            margin: 5px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: bold;
        }
        
        .language-btn.active {
            background-color: #5D5CDE;
            color: white;
        }
        
        .language-btn:hover:not(.active) {
            background-color: #eaeaea;
        }
        
        /* Header and navbar */
        .stApp header {
            background-color: transparent !important;
        }
        
        /* Custom sidebar */
        .css-1d391kg, .css-1r6slb0 {
            background-color: #f1f3f9;
        }
        
        /* Logo and title */
        .app-title {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #5D5CDE;
        }
        
        .app-logo {
            max-width: 80px;
            margin-bottom: 10px;
        }
        
        /* Navigation button */
        .nav-button {
            width: 100%;
            text-align: left;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 8px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
        }
        
        .nav-button:hover {
            background-color: rgba(93, 92, 222, 0.1);
        }
        
        .nav-button.active {
            background-color: #5D5CDE;
            color: white;
        }
        
        .nav-icon {
            margin-right: 10px;
            font-size: 1.2rem;
        }
        
        /* Welcome section */
        .welcome-heading {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            background: linear-gradient(90deg, #5D5CDE, #8A89FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .welcome-subheading {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
        }

        /* Quick start button */
        .quick-start-button {
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
            background-color: #f0f7ff;
            border: 2px solid #5D5CDE;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .quick-start-button:hover {
            background-color: #e0eeff;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(93, 92, 222, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "main"
if 'language' not in st.session_state:
    st.session_state.language = "ENG"
if 'camera' not in st.session_state:
    st.session_state.camera = False
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'uploaded_State' not in st.session_state:
    st.session_state.uploaded_State = False
if 'last_page' not in st.session_state:
    st.session_state.last_page = "main"

# Apply custom CSS
local_css()

# Function to get icon HTML
def get_icon(icon_name):
    return f'<span class="material-icons nav-icon">{icon_name}</span>'

# Function to create a navigation button
def nav_button(label, icon, page_name, lang):
    button_label = label[lang]
    active_class = "active" if st.session_state.page == page_name else ""
    
    if st.sidebar.button(
        f"{icon} {button_label}", 
        key=f"nav_{page_name}",
        use_container_width=True,
        type="primary" if st.session_state.page == page_name else "secondary"
    ):
        st.session_state.last_page = st.session_state.page
        st.session_state.page = page_name
        if st.session_state.quick_start_step != 5:
            st.session_state.personal_info_step = 1
            st.session_state.quick_start_step = 1
        st.rerun()

# Function to show the main page
def show_main():
    lang = st.session_state.language
    
    # Header section
    if lang == "ENG":
        st.markdown('<div class="welcome-heading">AI Traditional Chinese Medicine Assistant</div>', unsafe_allow_html=True)
        st.markdown('<div class="welcome-subheading">Discover personalized health insights through the wisdom of TCM</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="welcome-heading">AI中醫助手</div>', unsafe_allow_html=True)
        st.markdown('<div class="welcome-subheading">通過中醫智慧發現個性化健康見解</div>', unsafe_allow_html=True)
    
    # Quick Start Button - prominent at the top
    st.markdown(f"""
    <div class="quick-start-button">
        <div style="font-size: 24px; margin-bottom: 10px;">{'👋 New to TCM AI?' if lang == 'ENG' else '👋 初次使用中醫AI？'}</div>
        <div style="font-size: 16px; margin-bottom: 15px;">{'Get started with our guided setup to receive personalized TCM recommendations in just a few steps.' if lang == 'ENG' else '通過我們的引導式設置，只需幾個步驟即可獲得個性化的中醫建議。'}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(
        "🚀 " + ("Quick Start Guide" if lang == "ENG" else "快速入門指南"), 
        type="primary",
        use_container_width=True
    ):
        st.session_state.last_page = st.session_state.page
        st.session_state.page = "quick_start"
        if st.session_state.quick_start_step != 5:
            st.session_state.personal_info_step = 1
            st.session_state.quick_start_step = 1
        st.rerun()
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="feature-card" onclick="javascript:void(0)">
                <div class="feature-icon">👤</div>
                <div class="feature-title">{0}</div>
                <div class="feature-description">{1}</div>
                        
            </div>
            """.format(
                "Personal Information" if lang == "ENG" else "個人信息",
                "Manage your health profile and track your progress over time" if lang == "ENG" else "管理您的健康檔案並跟踪您的進步"
            ), unsafe_allow_html=True)
            
            if st.button("Go to Personal Info" if lang == "ENG" else "前往個人信息", use_container_width=True):
                st.session_state.last_page = st.session_state.page
                st.session_state.page = "Personal Info"
                st.rerun()
        
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">☁️</div>
                <div class="feature-title">{0}</div>
                <div class="feature-description">{1}</div>
            </div>
            """.format(
                "Weather Information" if lang == "ENG" else "天氣信息",
                "Get weather updates and TCM advice based on current conditions" if lang == "ENG" else "獲取天氣更新和基於當前狀況的中醫建議"
            ), unsafe_allow_html=True)
            
            if st.button("Go to Weather Info" if lang == "ENG" else "前往天氣信息", use_container_width=True):
                st.session_state.last_page = st.session_state.page
                st.session_state.page = "Weather Info"
                st.rerun()
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">👅</div>
                <div class="feature-title">{0}</div>
                <div class="feature-description">{1}</div>
            </div>
            """.format(
                "Tongue Diagnosis" if lang == "ENG" else "舌診",
                "Upload or capture a tongue image for AI-powered TCM diagnosis" if lang == "ENG" else "上傳或捕獲舌頭圖像進行AI驅動的中醫診斷"
            ), unsafe_allow_html=True)
            
            if st.button("Go to Tongue Detect" if lang == "ENG" else "前往舌診", use_container_width=True):
                st.session_state.last_page = st.session_state.page
                st.session_state.page = "Tongue Detect"
                st.rerun()
        
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🌿</div>
                <div class="feature-title">{0}</div>
                <div class="feature-description">{1}</div>
            </div>
            """.format(
                "Herbal Medicine Database" if lang == "ENG" else "藥材查詢",
                "Search and learn about traditional Chinese herbs and remedies" if lang == "ENG" else "搜索和了解中草藥和傳統療法"
            ), unsafe_allow_html=True)
            
            if st.button("Go to Herb Check" if lang == "ENG" else "前往藥材查詢", use_container_width=True):
                st.session_state.last_page = st.session_state.page
                st.session_state.page = "Herb Check"
                st.rerun()
    
    # Recommendation section
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💊</div>
        <div class="feature-title">{0}</div>
        <div class="feature-description">{1}</div>
    </div>
    """.format(
        "Personalized Recommendations" if lang == "ENG" else "個性化推薦",
        "Get customized TCM advice and treatment recommendations based on your health data" if lang == "ENG" else "根據您的健康數據獲取定制的中醫建議和治療推薦"
    ), unsafe_allow_html=True)
    
    if st.button("Go to Recommendation" if lang == "ENG" else "前往推薦", use_container_width=True):
        st.session_state.last_page = st.session_state.page
        st.session_state.page = "Recommendation"
        st.rerun()
    
    # Information section
    with st.expander("About this Application" if lang == "ENG" else "關於這個應用程序"):
        if lang == "ENG":
            st.write("""
            This AI-powered assistant provides personalized health advice and Traditional Chinese Medicine (TCM) 
            prescriptions based on your health condition. It combines modern technology with ancient TCM wisdom 
            to offer holistic health insights.
            
            Use the sidebar to navigate through different features:
            - **Personal Info**: Manage your health profile
            - **Tongue Detect**: Get TCM diagnosis from tongue images
            - **Weather Info**: Weather updates with TCM context
            - **Recommendation**: Receive personalized health recommendations
            - **Herb Check**: Learn about TCM herbs and their properties
            """)
        else:
            st.write("""
            這個AI驅動的助手根據您的健康狀況提供個性化的健康建議和中醫處方。它結合了現代技術和古老的中醫智慧，
            提供全面的健康見解。
            
            使用側邊欄導航不同功能：
            - **個人信息**：管理您的健康檔案
            - **舌診**：從舌頭圖像獲取中醫診斷
            - **天氣信息**：帶有中醫背景的天氣更新
            - **推薦**：獲取個性化健康推薦
            - **藥材查詢**：了解中藥材及其特性
            """)

# Improved sidebar with better UI
def show_sidebar():
    # App title and logo
    st.sidebar.markdown('<div class="app-title">🌿 TCM AI</div>', unsafe_allow_html=True)
    
    # Language selector
    st.sidebar.markdown("### " + ("Language" if st.session_state.language == "ENG" else "語言"))
    lang_col1, lang_col2 = st.sidebar.columns(2)
    
    with lang_col1:
        eng_active = "primary" if st.session_state.language == "ENG" else "secondary"
        if st.button("English", key="lang_eng", type=eng_active, use_container_width=True):
            st.session_state.language = "ENG"
            st.rerun()
    
    with lang_col2:
        cn_active = "primary" if st.session_state.language == "中文" else "secondary"
        if st.button("中文", key="lang_cn", type=cn_active, use_container_width=True):
            st.session_state.language = "中文"
            st.rerun()
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.markdown("### " + ("Navigation" if st.session_state.language == "ENG" else "導航"))
    
    # Define navigation items with localization
    nav_items = {
        "main": {
            "ENG": "Home",
            "中文": "首頁",
            "icon": "🏠"
        },
        "quick_start": {
            "ENG": "Quick Start",
            "中文": "快速入門",
            "icon": "🚀"
        },
        "Personal Info": {
            "ENG": "Personal Information",
            "中文": "個人信息",
            "icon": "👤"
        },
        "Tongue Detect": {
            "ENG": "Tongue Diagnosis",
            "中文": "舌診",
            "icon": "👅"
        },
        "Weather Info": {
            "ENG": "Weather Information",
            "中文": "天氣信息",
            "icon": "☁️"
        },
        "Recommendation": {
            "ENG": "Recommendations",
            "中文": "推薦",
            "icon": "💊"
        },
        "Herb Check": {
            "ENG": "Herb Database",
            "中文": "藥材查詢",
            "icon": "🌿"
        },
        "Herb Inventory": {
            "ENG": "Herb Inventory",
            "中文": "藥材庫存",
            "icon": "🧪"
        }
    }
    
    # Create navigation buttons
    for page_key, page_info in nav_items.items():
        nav_button(page_info, page_info["icon"], page_key, st.session_state.language)
    
    # Add herb inventory submenu if on the herb inventory page
    if st.session_state.page == "Herb Inventory":
        lang = st.session_state.language
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔹 " + ("Herb Inventory Menu" if lang == "ENG" else "藥材庫存菜單"))
        
        # Define menu options based on language
        menu_options = {
            "ENG": [
                "🌿 Add New Herb",
                "🔍 Search Herbs",
                "📦 Manage Inventory",
                "📊 Inventory Report",
                "📤 Export/Import Data"
            ],
            "中文": [
                "🌿 添加新藥材",
                "🔍 搜索藥材",
                "📦 管理庫存",
                "📊 庫存報告",
                "📤 導出/導入數據"
            ]
        }
        
        # Store the selected herb menu option in session state if not already present
        if 'herb_inventory_menu' not in st.session_state:
            st.session_state.herb_inventory_menu = menu_options[lang][0] if lang in menu_options else menu_options["ENG"][0]
        
        # Create the radio buttons for herb inventory submenu
        herb_menu = st.sidebar.radio(
            "", 
            menu_options[lang if lang in menu_options else "ENG"],
            key="herb_inventory_submenu"
        )
        
        # Update session state when menu changes
        if herb_menu != st.session_state.herb_inventory_menu:
            st.session_state.herb_inventory_menu = herb_menu
            st.rerun()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2024 AI TCM Assistant")
    st.sidebar.caption("Created by Enoch CHIU")

# Call sidebar function
show_sidebar()

# Scroll to top JavaScript - place at the beginning of each page load
if st.session_state.last_page != st.session_state.page:
    # This JavaScript will attempt to scroll to the top when the page changes
    st.markdown("""
    <script>
        // Attempt to scroll to top
        window.scrollTo(0, 0);
        
        // Alternative approach using requestAnimationFrame for more reliable scrolling
        window.addEventListener('load', function() {
            window.requestAnimationFrame(function() {
                window.scrollTo(0, 0);
            });
        });
    </script>
    """, unsafe_allow_html=True)
    
    # Reset the last_page to current page after scrolling attempt
    st.session_state.last_page = st.session_state.page

# Determine the current page
page = st.session_state.page

# Main content area
with st.container():
    if page == "main":
        show_main()
    elif page == "Personal Info":
        show_personal_info()
    elif page == "Tongue Detect":
        show_tongue_detect(client, model_name)
    elif page == "Weather Info":
        show_weather()
    elif page == "Recommendation":
        show_recommendation()
    elif page == "Herb Check":
        show_herb(client, model_name)
    elif page == "quick_start":
        show_quick_start(client, model_name)
    elif page == "Herb Inventory":
        show_herb_inventory()