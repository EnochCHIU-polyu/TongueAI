# herb_inventory.py

import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
import io
import matplotlib.pyplot as plt
import random
import base64
import time
from PIL import Image
import numpy as np

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

# Database connection and initialization
def connect_db():
    conn = sqlite3.connect("tcm_herbs.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS herbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            chinese_name TEXT,
            category TEXT,
            properties TEXT,
            meridians TEXT,
            stock_amount REAL,
            unit TEXT,
            storage_location TEXT,
            date_added TEXT,
            expiry_date TEXT,
            notes TEXT,
            image_path TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

# Store herb properties in dictionary format
def get_herb_properties_options():
    return {
        "Nature": ["Hot", "Warm", "Neutral", "Cool", "Cold"],
        "Flavor": ["Pungent", "Sweet", "Sour", "Bitter", "Salty"],
    }

# Get meridian options
def get_meridian_options():
    return [
        "Lung", "Large Intestine", "Stomach", "Spleen", 
        "Heart", "Small Intestine", "Bladder", "Kidney",
        "Pericardium", "Triple Burner", "Gallbladder", "Liver"
    ]

# Get herb category options
def get_category_options():
    return [
        "Exterior-Releasing Herbs", "Heat-Clearing Herbs", 
        "Downward-Draining Herbs", "Wind-Damp Dispelling Herbs",
        "Aromatic Herbs for Dampness", "Dampness-Draining Diuretic Herbs",
        "Interior-Warming Herbs", "Qi-Regulating Herbs",
        "Digestant Herbs", "Worm-Expelling Herbs",
        "Blood-Regulating Herbs", "Cough-Suppressing & Panting-Calming Herbs",
        "Tranquilizing Herbs", "Liver-Calming Herbs",
        "Orifice-Opening Herbs", "Tonic Herbs",
        "Astringent Herbs", "Emetic Herbs",
        "External Use Herbs"
    ]

# OCR Recognition - simulated since easyocr isn't included
def scan_herb_label(img_path):
    try:
        # In a real implementation, you would use EasyOCR here
        # For now, we'll return a simulated result
        common_herbs = [
            "Ginseng (人參)", "Astragalus (黃芪)", "Licorice (甘草)", 
            "Angelica (當歸)", "Rehmannia (熟地黃)", "Cinnamon (肉桂)",
            "Ginger (生薑)", "Jujube (大棗)", "Chrysanthemum (菊花)",
            "Schisandra (五味子)", "Coptis (黃連)", "Peony (白芍)"
        ]
        return random.choice(common_herbs)
    except:
        return None

# Save uploaded image
def save_uploaded_image(uploaded_file):
    if uploaded_file is None:
        return None
    
    # Create directories if they don't exist
    if not os.path.exists("herb_images"):
        os.makedirs("herb_images")
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_number = random.randint(1000, 9999)
    file_extension = os.path.splitext(uploaded_file.name)[1]
    filename = f"herb_images/herb_{timestamp}_{random_number}{file_extension}"
    
    # Save the image
    with open(filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return filename

# Store herb information
def store_herb(name, chinese_name, category, properties, meridians, stock_amount, unit, storage_location, expiry_date, notes, image_path):
    conn, cursor = connect_db()
    try:
        cursor.execute("""
            INSERT INTO herbs (name, chinese_name, category, properties, meridians, stock_amount, unit, 
            storage_location, date_added, expiry_date, notes, image_path) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, chinese_name, category, properties, meridians, stock_amount, unit, 
            storage_location, datetime.now().strftime("%Y-%m-%d"), expiry_date, notes, image_path
        ))
        conn.commit()
        st.success(f"✅ Herb `{name}` has been successfully added to inventory!")
    except sqlite3.IntegrityError:
        st.warning(f"⚠️ Herb `{name}` already exists in database. Please use Update function instead.")
    conn.close()

# Query all herbs
def query_herbs():
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM herbs")
    results = cursor.fetchall()
    conn.close()
    return results

# Get herb details by name
def get_herb_by_name(name):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM herbs WHERE name=?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result

# Update herb information
def update_herb(id, name, chinese_name, category, properties, meridians, stock_amount, unit, storage_location, expiry_date, notes, image_path):
    conn, cursor = connect_db()
    try:
        # Only update image if a new one is provided
        if image_path:
            cursor.execute("""
                UPDATE herbs SET name=?, chinese_name=?, category=?, properties=?, meridians=?, 
                stock_amount=?, unit=?, storage_location=?, expiry_date=?, notes=?, image_path=?
                WHERE id=?
            """, (
                name, chinese_name, category, properties, meridians, stock_amount, unit, 
                storage_location, expiry_date, notes, image_path, id
            ))
        else:
            # Don't update the image_path if not provided
            cursor.execute("""
                UPDATE herbs SET name=?, chinese_name=?, category=?, properties=?, meridians=?, 
                stock_amount=?, unit=?, storage_location=?, expiry_date=?, notes=?
                WHERE id=?
            """, (
                name, chinese_name, category, properties, meridians, stock_amount, unit, 
                storage_location, expiry_date, notes, id
            ))
        conn.commit()
        st.success(f"✅ Herb `{name}` has been successfully updated!")
    except Exception as e:
        st.error(f"Error updating herb: {e}")
    conn.close()

# Delete herb from database
def delete_herb(name):
    conn, cursor = connect_db()
    cursor.execute("SELECT image_path FROM herbs WHERE name=?", (name,))
    result = cursor.fetchone()
    
    # Delete the image file if it exists
    if result and result[0] and os.path.exists(result[0]):
        try:
            os.remove(result[0])
        except:
            pass
    
    cursor.execute("DELETE FROM herbs WHERE name=?", (name,))
    conn.commit()
    conn.close()
    st.error(f"🗑️ Herb `{name}` has been deleted from inventory.")

# Update herb stock
def update_herb_stock(name, new_amount):
    conn, cursor = connect_db()
    cursor.execute("UPDATE herbs SET stock_amount=? WHERE name=?", (new_amount, name))
    conn.commit()
    conn.close()
    st.success(f"✅ Stock for `{name}` has been updated to {new_amount}.")

# Export data to CSV
def export_herb_data():
    conn, cursor = connect_db()
    df = pd.read_sql_query("SELECT * FROM herbs", conn)
    conn.close()
    
    # Create export directory if it doesn't exist
    if not os.path.exists("exports"):
        os.makedirs("exports")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exports/tcm_herbs_export_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    
    return filename

# Import data from CSV
def import_herb_data(file):
    conn, cursor = connect_db()
    try:
        df = pd.read_csv(file)
        # Remove the ID column if present to avoid conflicts
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
        
        # Insert data one by one to handle potential conflicts
        for _, row in df.iterrows():
            try:
                columns = ', '.join(row.index)
                placeholders = ', '.join(['?'] * len(row))
                values = tuple(row.values)
                
                query = f"INSERT OR IGNORE INTO herbs ({columns}) VALUES ({placeholders})"
                cursor.execute(query, values)
            except Exception as e:
                print(f"Error importing row: {e}")
                continue
                
        conn.commit()
        st.success(f"✅ Successfully imported {len(df)} herbs into the database!")
    except Exception as e:
        st.error(f"Error importing data: {e}")
    finally:
        conn.close()

# Search herbs by multiple criteria
def search_herbs(search_term=None, category=None, property=None, meridian=None):
    conn, cursor = connect_db()
    
    query = "SELECT * FROM herbs WHERE 1=1"
    params = []
    
    if search_term:
        query += " AND (name LIKE ? OR chinese_name LIKE ? OR notes LIKE ?)"
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if category and category != "All Categories":
        query += " AND category = ?"
        params.append(category)
    
    if property and property != "All Properties":
        query += " AND properties LIKE ?"
        params.append(f"%{property}%")
    
    if meridian and meridian != "All Meridians":
        query += " AND meridians LIKE ?"
        params.append(f"%{meridian}%")
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# Generate inventory report with visualization
def generate_inventory_report():
    conn, cursor = connect_db()
    
    # Get herbs by category
    cursor.execute("SELECT category, COUNT(*) FROM herbs GROUP BY category")
    category_data = cursor.fetchall()
    
    # Get herbs by expiry date (upcoming expirations within 6 months)
    six_months_later = (datetime.now() + pd.DateOffset(months=6)).strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT name, expiry_date FROM herbs WHERE expiry_date <= ? ORDER BY expiry_date",
        (six_months_later,)
    )
    expiring_herbs = cursor.fetchall()
    
    # Get herbs with low stock (less than 50g or 10 units)
    cursor.execute(
        "SELECT name, stock_amount, unit FROM herbs WHERE stock_amount <= CASE WHEN unit='g' THEN 50 WHEN unit='ml' THEN 50 ELSE 10 END"
    )
    low_stock_herbs = cursor.fetchall()
    
    conn.close()
    
    # Create category distribution chart
    if category_data:
        categories = [row[0] for row in category_data]
        counts = [row[1] for row in category_data]
        
        # Create figure with custom colors
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.viridis(np.linspace(0, 0.9, len(categories)))
        bars = ax.bar(categories, counts, color=colors)
        ax.set_xlabel('Herb Categories')
        ax.set_ylabel('Number of Herbs')
        ax.set_title('Herb Distribution by Category')
        plt.xticks(rotation=45, ha='right')
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Convert plot to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        
        # Create report object
        report = {
            'category_chart': buf,
            'expiring_herbs': expiring_herbs,
            'low_stock_herbs': low_stock_herbs
        }
        
        return report
    else:
        return None

# Show herb detail card
def show_herb_detail_card(herb):
    if not herb:
        return
    
    # Unpack herb data
    id, name, chinese_name, category, properties, meridians, stock_amount, unit, storage_location, date_added, expiry_date, notes, image_path = herb
    
    # Create columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display herb image if available
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption=f"{name} ({chinese_name})", width=200)
        else:
            st.info("No image available")
    
    with col2:
        # Create styled info card with colored borders based on properties
        property_color = "#5D5CDE"  # Default purple color
        if "Hot" in properties or "Warm" in properties:
            property_color = "#e74c3c"  # Red for hot/warm
        elif "Cool" in properties or "Cold" in properties:
            property_color = "#3498db"  # Blue for cool/cold
        
        st.markdown(f"""
        <div style="border-left: 5px solid {property_color}; padding-left: 15px; margin-bottom: 20px;">
            <h3 style="margin-bottom: 5px;">{name}</h3>
            <h4 style="margin-top: 0; color: #666; font-weight: normal;">{chinese_name}</h4>
            
            <div style="display: flex; margin-top: 15px; font-size: 0.9rem;">
                <div style="flex: 1;">
                    <div style="margin-bottom: 8px;"><strong>Category:</strong> {category}</div>
                    <div style="margin-bottom: 8px;"><strong>Properties:</strong> {properties}</div>
                    <div style="margin-bottom: 8px;"><strong>Meridians:</strong> {meridians}</div>
                </div>
                <div style="flex: 1;">
                    <div style="margin-bottom: 8px;"><strong>Stock:</strong> {stock_amount} {unit}</div>
                    <div style="margin-bottom: 8px;"><strong>Location:</strong> {storage_location}</div>
                    <div style="margin-bottom: 8px;"><strong>Expiry:</strong> {expiry_date}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show notes if available
        if notes:
            st.markdown(f"**Notes:**  \n{notes}")

# Modified Add New Herb section with integrated AI recognition and manual entry

def show_herb_inventory(client, model_name):
    lang = st.session_state.language  # Get current language

    # Set page title based on language
    page_title = "TCM Herb Inventory Management" if lang == "ENG" else "中藥材庫存管理"
    
    # Initialize session state for herb management
    if 'selected_herb_name' not in st.session_state:
        st.session_state.selected_herb_name = None
    if 'selected_storage' not in st.session_state:
        st.session_state.selected_storage = None
    if 'herb_image' not in st.session_state:
        st.session_state.herb_image = None
    if 'herb_ai_result' not in st.session_state:
        st.session_state.herb_ai_result = None
    if 'ai_loading' not in st.session_state:
        st.session_state.ai_loading = False
    if 'has_confirmed_ai_result' not in st.session_state:
        st.session_state.has_confirmed_ai_result = False
        
    st.markdown(f"<h1 style='color: #5D5CDE;'>{page_title}</h1>", unsafe_allow_html=True)
    
    # Get the selected menu option from session state
    selected_menu = st.session_state.herb_inventory_menu
    
    # Add New Herb section with integrated AI Recognition
    if selected_menu == "🌿 Add New Herb" or selected_menu == "🌿 添加新藥材":
        st.subheader("🌿 " + ("Add New Herb to Inventory" if lang == "ENG" else "添加新藥材到庫存"))
        
        # Create a container with border for AI Recognition
        with st.container(border=True):
            st.markdown(f"### 🔍 {('AI Recognition' if lang == 'ENG' else 'AI識別')}")
            st.markdown(("Use your camera to scan herbs and let AI identify them" if lang == "ENG" else "使用您的相機掃描藥材，讓AI識別它們"))
            
            # Camera input
            camera_image = st.camera_input(
                "Take a photo of herbs" if lang == "ENG" else "拍攝藥材照片",
                help="Position the herbs clearly in the frame" if lang == "ENG" else "請將藥材清晰地放在框架中"
            )
            
            # Alternative file upload
            st.markdown("**OR**")
            uploaded_file = st.file_uploader(
                "Upload herb image" if lang == "ENG" else "上傳藥材圖片",
                type=["jpg", "jpeg", "png"]
            )
            
            # Use either camera image or uploaded file
            if camera_image is not None:
                st.session_state.herb_image = camera_image
            elif uploaded_file is not None:
                st.session_state.herb_image = uploaded_file
            
            # Analyze and Clear buttons - positioned below both inputs
            if st.session_state.herb_image and not st.session_state.ai_loading:
                analyze_col, clear_col = st.columns(2)
                
                with analyze_col:
                    if st.button("🔍 " + ("Analyze Herb" if lang == "ENG" else "分析藥材"), 
                               key="analyze_herb_button",
                               type="primary",
                               use_container_width=True):
                        st.session_state.ai_loading = True
                        st.session_state.has_confirmed_ai_result = False
                        
                        # Save the image to a temp file for analysis
                        temp_image_path = "herb_temp_image.jpg"
                        with open(temp_image_path, "wb") as f:
                            f.write(st.session_state.herb_image.getbuffer())
                        
                        # Define AI prompts based on language
                        if lang == "ENG":
                            user_prompt = ("Analyze this herb image and return the following information in JSON format: "
                                         "herb name in English, Chinese name, category (Traditional Chinese Medicine, "
                                         "Western Medicine, or Health Products), and a brief note about its properties and uses.")
                            system_prompt = (
                                "You are an expert in traditional Chinese medicine herb identification. "
                                "Analyze the herb image and provide ONLY the following information in JSON format:\n"
                                "{\n"
                                "  \"herb_name\": \"[English name of the herb]\",\n"
                                "  \"chinese_name\": \"[Chinese characters for the herb]\",\n"
                                "  \"category\": \"[one of: Traditional Chinese Medicine, Western Medicine, Health Products]\",\n"
                                "  \"notes\": \"[brief description of herb properties and uses]\"\n"
                                "}\n\n"
                                "Do not include any explanatory text outside the JSON structure."
                            )
                        else:
                            user_prompt = ("分析這個藥材圖片，並以JSON格式返回以下信息："
                                         "英文藥材名稱，中文名稱，類別（中藥、西藥或保健品），以及關於其性質和用途的簡短說明。")
                            system_prompt = (
                                "您是中藥材識別專家。分析藥材圖片，僅提供以下JSON格式的信息：\n"
                                "{\n"
                                "  \"herb_name\": \"[藥材的英文名稱]\",\n"
                                "  \"chinese_name\": \"[藥材的中文字符]\",\n"
                                "  \"category\": \"[選擇其一: 中藥, 西藥, 保健品]\",\n"
                                "  \"notes\": \"[藥材性質和用途的簡短描述]\"\n"
                                "}\n\n"
                                "請不要在JSON結構外包含任何解釋性文本。"
                            )
                        
                        # Placeholder for Azure AI API call
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
                            
                            # Extract result
                            result = response.choices[0].message.content
                            
                            # Clean up any extra text and parse JSON
                            import json
                            import re
                            
                            # Try to extract JSON portion
                            json_pattern = r'\{[\s\S]*\}'
                            json_match = re.search(json_pattern, result)
                            
                            if json_match:
                                json_str = json_match.group(0)
                                try:
                                    herb_data = json.loads(json_str)
                                    st.session_state.herb_ai_result = herb_data
                                except json.JSONDecodeError:
                                    st.session_state.herb_ai_result = {
                                        "error": "Could not parse JSON result",
                                        "raw_result": result
                                    }
                            else:
                                st.session_state.herb_ai_result = {
                                    "error": "No JSON found in response",
                                    "raw_result": result
                                }
           
                        except Exception as e:
                            st.session_state.herb_ai_result = {"error": str(e)}
                        
                        # Turn off loading state
                        st.session_state.ai_loading = False
                        st.rerun()
                
                with clear_col:
                    if st.button("🗑️ " + ("Clear Image" if lang == "ENG" else "清除圖片"), 
                               key="clear_image",
                               use_container_width=True):
                        st.session_state.herb_image = None
                        st.session_state.herb_ai_result = None
                        st.session_state.has_confirmed_ai_result = False
                        st.rerun()
            
            # Display AI results or loading indicator
            if st.session_state.ai_loading:
                st.spinner(("Analyzing herb..." if lang == "ENG" else "分析藥材中..."))
            
            elif st.session_state.herb_ai_result:
                result = st.session_state.herb_ai_result
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                    if "raw_result" in result:
                        with st.expander("Show raw response"):
                            st.text(result["raw_result"])
                else:
                    # Display the recognized herb information in a styled card
                    st.success(("Herb recognized!" if lang == "ENG" else "藥材已識別！"))
                    
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 15px 0;">
                        <h3 style="margin-top: 0; color: #5D5CDE;">{result.get('herb_name', 'Unknown')} ({result.get('chinese_name', '未知')})</h3>
                        <p><strong>{"Category" if lang == "ENG" else "類別"}:</strong> {result.get('category', 'Unknown')}</p>
                        <p><strong>{"Notes" if lang == "ENG" else "備註"}:</strong> {result.get('notes', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Confirm button to use in form
                    confirm_col = st.columns(1)[0]
                    with confirm_col:
                        confirm_text = "✅ Confirm & Use in Form" if lang == "ENG" else "✅ 確認並使用"
                        if st.button(confirm_text, key="confirm_ai_result", type="primary", use_container_width=True):
                            st.session_state.has_confirmed_ai_result = True
                            st.info(("Information confirmed! Scroll down to complete the form." if lang == "ENG" else "信息已確認！請向下滾動完成表單。"))
                            # We leave the herb_ai_result in session_state so it can be used by the form
        
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Manual Entry Section heading with icon
        st.markdown(f"### 📝 {('Manual Entry' if lang == 'ENG' else '手動輸入')}")
        
        # Storage location selector
        st.markdown("#### " + ("Select Storage Location" if lang == "ENG" else "選擇存儲位置"))
        
        # Create a 3x3 grid of large location buttons with fixed height for consistency
        btn_style = """
        <style>
            .storage-button {
                height: 70px;
                font-size: 20px !important;
                font-weight: bold !important;
            }
        </style>
        """
        st.markdown(btn_style, unsafe_allow_html=True)
        
        # Create a 3x3 grid of location buttons
        col1, col2, col3 = st.columns(3)
        
        # Row 1
        with col1:
            btn_a1_type = "primary" if st.session_state.selected_storage == "A1" else "secondary"
            if st.button("A1", key="loc_A1", use_container_width=True, type=btn_a1_type, 
                       help="Storage location A1"):
                st.session_state.selected_storage = "A1"
                st.rerun()
        
        with col2:
            btn_a2_type = "primary" if st.session_state.selected_storage == "A2" else "secondary"
            if st.button("A2", key="loc_A2", use_container_width=True, type=btn_a2_type,
                       help="Storage location A2"):
                st.session_state.selected_storage = "A2"
                st.rerun()
        
        with col3:
            btn_a3_type = "primary" if st.session_state.selected_storage == "A3" else "secondary"
            if st.button("A3", key="loc_A3", use_container_width=True, type=btn_a3_type,
                       help="Storage location A3"):
                st.session_state.selected_storage = "A3"
                st.rerun()
        
        # Row 2
        with col1:
            btn_b1_type = "primary" if st.session_state.selected_storage == "B1" else "secondary"
            if st.button("B1", key="loc_B1", use_container_width=True, type=btn_b1_type,
                       help="Storage location B1"):
                st.session_state.selected_storage = "B1"
                st.rerun()
        
        with col2:
            btn_b2_type = "primary" if st.session_state.selected_storage == "B2" else "secondary"
            if st.button("B2", key="loc_B2", use_container_width=True, type=btn_b2_type,
                       help="Storage location B2"):
                st.session_state.selected_storage = "B2"
                st.rerun()
        
        with col3:
            btn_b3_type = "primary" if st.session_state.selected_storage == "B3" else "secondary"
            if st.button("B3", key="loc_B3", use_container_width=True, type=btn_b3_type,
                       help="Storage location B3"):
                st.session_state.selected_storage = "B3"
                st.rerun()
        
        # Row 3
        with col1:
            btn_c1_type = "primary" if st.session_state.selected_storage == "C1" else "secondary"
            if st.button("C1", key="loc_C1", use_container_width=True, type=btn_c1_type,
                       help="Storage location C1"):
                st.session_state.selected_storage = "C1"
                st.rerun()
        
        with col2:
            btn_c2_type = "primary" if st.session_state.selected_storage == "C2" else "secondary"
            if st.button("C2", key="loc_C2", use_container_width=True, type=btn_c2_type,
                       help="Storage location C2"):
                st.session_state.selected_storage = "C2"
                st.rerun()
        
        with col3:
            btn_c3_type = "primary" if st.session_state.selected_storage == "C3" else "secondary"
            if st.button("C3", key="loc_C3", use_container_width=True, type=btn_c3_type,
                       help="Storage location C3"):
                st.session_state.selected_storage = "C3"
                st.rerun()
        
        # Show the currently selected location
        if st.session_state.selected_storage:
            st.success(f"Selected location: {st.session_state.selected_storage}")
        else:
            st.warning(("Please select a storage location" if lang == "ENG" else "請選擇存儲位置"))
        
        # Get default values from AI result if user has confirmed it
        default_herb_name = ""
        default_chinese_name = ""
        default_category = 0  # Index for default selection
        default_notes = ""
        
        if st.session_state.has_confirmed_ai_result and st.session_state.herb_ai_result and "error" not in st.session_state.herb_ai_result:
            result = st.session_state.herb_ai_result
            default_herb_name = result.get('herb_name', '')
            default_chinese_name = result.get('chinese_name', '')
            
            # Set category index based on AI result
            simple_categories = [
                "Traditional Chinese Medicine", 
                "Western Medicine", 
                "Health Products"
            ]
            if lang != "ENG":
                simple_categories = ["中藥", "西藥", "保健品"]
            
            ai_category = result.get('category', '')
            if ai_category in simple_categories:
                default_category = simple_categories.index(ai_category)
            
            default_notes = result.get('notes', '')
        
        # Main form with simplified fields
        with st.form("simple_herb_form"):
            # Two columns for basic info
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    ("Herb Name (English)" if lang == "ENG" else "藥材名稱（英文）"),
                    value=default_herb_name
                )
                
                # Simplified category options
                simple_categories = [
                    "Traditional Chinese Medicine", 
                    "Western Medicine", 
                    "Health Products"
                ]
                if lang != "ENG":
                    simple_categories = ["中藥", "西藥", "保健品"]
                    
                category = st.selectbox(
                    ("Category" if lang == "ENG" else "類別"), 
                    simple_categories,
                    index=default_category
                )
                
            with col2:
                chinese_name = st.text_input(
                    ("Chinese Name" if lang == "ENG" else "中文名稱"),
                    value=default_chinese_name
                )
                expiry_date = st.date_input(
                    ("Expiry Date" if lang == "ENG" else "有效期"), 
                    min_value=datetime.now().date()
                )
            
            # Stock amount field
            stock_amount = st.number_input(
                ("Stock Amount" if lang == "ENG" else "庫存量"), 
                min_value=0.0, 
                step=0.1, 
                value=0.0
            )
            
            # Notes field with default from AI if available
            notes = st.text_area(
                ("Notes (optional)" if lang == "ENG" else "備註（可選）"), 
                value=default_notes,
                height=80
            )
            
            # Display the selected location inside the form (read-only)
            storage_location = st.session_state.selected_storage
            st.markdown(f"**Storage location:** {storage_location if storage_location else '(None selected)'}")
            
            # Submit button
            submit_button = st.form_submit_button(
                ("✅ Add Herb to Inventory" if lang == "ENG" else "✅ 添加藥材到庫存"), 
                use_container_width=True
            )
            
            if submit_button:
                if not name.strip():
                    st.warning("⚠️ " + ("Herb name cannot be empty." if lang == "ENG" else "藥材名稱不能為空。"))
                elif not storage_location:
                    st.warning("⚠️ " + ("Please select a storage location." if lang == "ENG" else "請選擇存儲位置。"))
                else:
                    # Simplified properties and meridians
                    properties = "Neutral" if lang == "ENG" else "平"
                    meridians = ""
                    unit = "g"
                    
                    # Store herb in database
                    store_herb(
                        name, 
                        chinese_name, 
                        category, 
                        properties, 
                        meridians, 
                        stock_amount, 
                        unit, 
                        storage_location, 
                        expiry_date, 
                        notes, 
                        None  # No image for simplified version
                    )
                    
                    # Reset the form and AI results
                    st.session_state.selected_storage = None
                    st.session_state.herb_image = None
                    st.session_state.herb_ai_result = None
                    st.session_state.has_confirmed_ai_result = False
                    st.rerun()
        
        # Add a reset button for the form
        if st.button("🔄 Reset Form", use_container_width=True):
            st.session_state.selected_storage = None
            st.session_state.herb_image = None
            st.session_state.herb_ai_result = None
            st.session_state.has_confirmed_ai_result = False
            st.rerun()



    # Search Herbs section
    elif selected_menu == "🔍 Search Herbs" or selected_menu == "🔍 搜索藥材":
        st.subheader("🔍 " + ("Search Herbs" if lang == "ENG" else "搜索藥材"))
        
        # Search filters in a single row
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            search_term = st.text_input(("Search for herb" if lang == "ENG" else "搜索藥材"), 
                                       placeholder=("Name, Chinese name, or notes" if lang == "ENG" else "名稱，中文名或備註"))
        
        with col2:
            categories = ["All Categories"] + get_category_options()
            category_filter = st.selectbox(("Category" if lang == "ENG" else "類別"), categories)
        
        with col3:
            properties = ["All Properties"] + get_herb_properties_options()["Nature"]
            property_filter = st.selectbox(("Nature" if lang == "ENG" else "性質"), properties)
        
        with col4:
            meridians = ["All Meridians"] + get_meridian_options()
            meridian_filter = st.selectbox(("Meridian" if lang == "ENG" else "歸經"), meridians)
        
        # Search button
        if st.button("🔍 " + ("Search" if lang == "ENG" else "搜索"), use_container_width=True):
            search_results = search_herbs(
                search_term, 
                None if category_filter == "All Categories" else category_filter,
                None if property_filter == "All Properties" else property_filter,
                None if meridian_filter == "All Meridians" else meridian_filter
            )
            
            if search_results:
                st.success(f"🌿 " + (f"Found {len(search_results)} herbs" if lang == "ENG" else f"找到 {len(search_results)} 種藥材"))
                
                # Display results in a table format
                df = pd.DataFrame(search_results, columns=[
                    "ID", "Name", "Chinese Name", "Category", "Properties", "Meridians",
                    "Stock", "Unit", "Location", "Date Added", "Expiry Date", "Notes", "Image Path"
                ])
                
                # Select only relevant columns for display
                display_df = df[["Name", "Chinese Name", "Category", "Properties", "Stock", "Unit", "Location"]]
                st.dataframe(display_df, use_container_width=True)
                
                # Allow selecting a herb for detailed view
                selected_herb_index = st.selectbox(
                    ("Select herb to view details" if lang == "ENG" else "選擇藥材查看詳情"),
                    options=range(len(search_results)),
                    format_func=lambda x: f"{search_results[x][1]} ({search_results[x][2]})"
                )
                
                # Show detailed information for selected herb
                if selected_herb_index is not None:
                    st.markdown("---")
                    st.subheader("🌿 " + ("Herb Details" if lang == "ENG" else "藥材詳情"))
                    show_herb_detail_card(search_results[selected_herb_index])
            else:
                st.warning("🔍 " + ("No herbs found matching your search criteria." if lang == "ENG" else "沒有找到符合您搜索條件的藥材。"))
    
    # Manage Inventory section
    elif selected_menu == "📦 Manage Inventory" or selected_menu == "📦 管理庫存":
        st.subheader("📦 " + ("Manage Inventory" if lang == "ENG" else "管理庫存"))
        
        # Sub-tabs for different inventory operations
        inventory_tab = st.radio(
            ("Select operation" if lang == "ENG" else "選擇操作"),
            [
                ("Update Herb Information" if lang == "ENG" else "更新藥材信息"),
                ("Adjust Stock Levels" if lang == "ENG" else "調整庫存水平"),
                ("Remove Herb" if lang == "ENG" else "移除藥材")
            ],
            horizontal=True
        )
        
        # Get all herbs for selection
        all_herbs = query_herbs()
        
        if not all_herbs:
            st.warning("📭 " + ("No herbs in inventory. Add some herbs first." if lang == "ENG" else "庫存中沒有藥材。請先添加一些藥材。"))
        else:
            # Create a list of herb names for selection
            herb_options = [(herb[1], herb[2]) for herb in all_herbs]
            
            # Format function to display both English and Chinese names
            def format_herb_name(idx):
                name, chinese_name = herb_options[idx]
                return f"{name} ({chinese_name})"
            
            # Select herb to manage
            selected_herb_index = st.selectbox(
                ("Select herb" if lang == "ENG" else "選擇藥材"),
                options=range(len(herb_options)),
                format_func=format_herb_name
            )
            
            # Get selected herb's details
            selected_herb = all_herbs[selected_herb_index]
            
            # Update Herb Information
            if inventory_tab == ("Update Herb Information" if lang == "ENG" else "更新藥材信息"):
                st.markdown("### " + ("Update Herb Information" if lang == "ENG" else "更新藥材信息"))
                
                # Unpack herb data
                id, name, chinese_name, category, properties, meridians, stock_amount, unit, storage_location, date_added, expiry_date, notes, image_path = selected_herb
                
                # Show current image if available
                if image_path and os.path.exists(image_path):
                    st.image(image_path, caption=f"{name} ({chinese_name})", width=200)
                
                # Upload new image
                new_image = st.file_uploader(
                    ("Upload new image (optional)" if lang == "ENG" else "上傳新圖片（可選）"), 
                    type=["jpg", "png", "jpeg"]
                )
                
                # Form for updating herb details
                with st.form("update_herb_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        updated_name = st.text_input(("Herb Name (English)" if lang == "ENG" else "藥材名稱（英文）"), value=name)
                        updated_chinese_name = st.text_input(("Chinese Name" if lang == "ENG" else "中文名稱"), value=chinese_name)
                        
                        # Extract current nature and flavor
                        current_properties = properties.split(', ')
                        current_nature = current_properties[0] if current_properties else ""
                        
                        # Category dropdown
                        categories = get_category_options()
                        category_index = categories.index(category) if category in categories else 0
                        updated_category = st.selectbox(("Category" if lang == "ENG" else "類別"), categories, index=category_index)
                        
                        # Properties
                        properties_options = get_herb_properties_options()
                        nature_options = [""] + properties_options["Nature"]
                        nature_index = nature_options.index(current_nature) if current_nature in nature_options else 0
                        updated_nature = st.selectbox(("Nature" if lang == "ENG" else "性質"), nature_options, index=nature_index)
                        
                        # Current flavors
                        current_flavors = [p.strip() for p in current_properties[1:] if p.strip() in properties_options["Flavor"]]
                        updated_flavor = st.multiselect(("Flavor" if lang == "ENG" else "味道"), properties_options["Flavor"], default=current_flavors)
                        
                        # Combine properties
                        updated_properties = f"{updated_nature}, {', '.join(updated_flavor)}" if updated_flavor else updated_nature
                    
                    with col2:
                        # Meridians multiselect
                        meridian_options = get_meridian_options()
                        current_meridians = [m.strip() for m in meridians.split(',') if m.strip() in meridian_options]
                        updated_meridians = st.multiselect(("Meridians" if lang == "ENG" else "歸經"), meridian_options, default=current_meridians)
                        updated_meridians_text = ", ".join(updated_meridians)
                        
                        # Stock amount and unit
                        stock_col1, stock_col2 = st.columns([2, 1])
                        with stock_col1:
                            updated_stock_amount = st.number_input(("Stock Amount" if lang == "ENG" else "庫存量"), 
                                                                min_value=0.0, step=0.1, value=float(stock_amount))
                        with stock_col2:
                            unit_options = ["g", "ml", "pieces", "packets"]
                            unit_index = unit_options.index(unit) if unit in unit_options else 0
                            updated_unit = st.selectbox(("Unit" if lang == "ENG" else "單位"), unit_options, index=unit_index)
                        
                        # Storage location
                        location_options = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2", "D3"]
                        location_index = location_options.index(storage_location) if storage_location in location_options else 0
                        updated_storage_location = st.selectbox(("Storage Location" if lang == "ENG" else "存儲位置"), 
                                                             location_options, index=location_index)
                        
                        # Expiry date
                        updated_expiry_date = st.date_input(("Expiry Date" if lang == "ENG" else "有效期"), 
                                                         value=datetime.strptime(expiry_date, '%Y-%m-%d').date() 
                                                         if expiry_date else datetime.now().date())
                    
                    # Notes field
                    updated_notes = st.text_area(("Notes" if lang == "ENG" else "備註"), value=notes, height=100)
                    
                    # Submit button
                    update_button = st.form_submit_button(("✅ Update Herb Information" if lang == "ENG" else "✅ 更新藥材信息"))
                    
                    if update_button:
                        if updated_name.strip():
                            # Save the new uploaded image if available
                            new_image_path = save_uploaded_image(new_image) if new_image else None
                            
                            # Update herb in database
                            update_herb(
                                id, updated_name, updated_chinese_name, updated_category, 
                                updated_properties, updated_meridians_text, updated_stock_amount, 
                                updated_unit, updated_storage_location, updated_expiry_date, 
                                updated_notes, new_image_path
                            )
                            
                            # Refresh the page to show updated information
                            st.rerun()
                        else:
                            st.warning("⚠️ " + ("Herb name cannot be empty." if lang == "ENG" else "藥材名稱不能為空。"))
            
            # Adjust Stock Levels
            elif inventory_tab == ("Adjust Stock Levels" if lang == "ENG" else "調整庫存水平"):
                st.markdown("### " + ("Adjust Stock Levels" if lang == "ENG" else "調整庫存水平"))
                
                # Unpack selected herb data
                id, name, chinese_name, category, properties, meridians, stock_amount, unit, storage_location, date_added, expiry_date, notes, image_path = selected_herb
                
                # Display current stock information
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <h4 style="margin-top: 0;">{name} ({chinese_name})</h4>
                    <p><strong>{"Current Stock" if lang == "ENG" else "當前庫存"}:</strong> {stock_amount} {unit}</p>
                    <p><strong>{"Location" if lang == "ENG" else "位置"}:</strong> {storage_location}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Stock adjustment options
                adjustment_type = st.radio(
                    ("Adjustment Type" if lang == "ENG" else "調整類型"),
                    [
                        ("Add Stock" if lang == "ENG" else "添加庫存"),
                        ("Remove Stock" if lang == "ENG" else "減少庫存"),
                        ("Set Stock Level" if lang == "ENG" else "設定庫存水平")
                    ]
                )
                
                # Input for adjustment amount
                adjustment_amount = st.number_input(
                    ("Amount" if lang == "ENG" else "數量"),
                    min_value=0.0,
                    step=0.1,
                    value=0.0
                )
                
                # Calculate new stock level based on adjustment type
                new_stock_level = stock_amount
                if adjustment_type == ("Add Stock" if lang == "ENG" else "添加庫存"):
                    new_stock_level = stock_amount + adjustment_amount
                elif adjustment_type == ("Remove Stock" if lang == "ENG" else "減少庫存"):
                    new_stock_level = max(0, stock_amount - adjustment_amount)
                elif adjustment_type == ("Set Stock Level" if lang == "ENG" else "設定庫存水平"):
                    new_stock_level = adjustment_amount
                
                # Display new stock level
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 10px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>{"New Stock Level" if lang == "ENG" else "新庫存水平"}:</strong> {new_stock_level} {unit}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Reason for adjustment
                adjustment_reason = st.text_area(
                    ("Reason for adjustment (optional)" if lang == "ENG" else "調整原因（可選）"), 
                    height=80
                )
                
                # Submit button
                if st.button("✅ " + ("Confirm Stock Adjustment" if lang == "ENG" else "確認庫存調整"), use_container_width=True):
                    # Update stock level in database
                    update_herb_stock(name, new_stock_level)
                    
                    # Update notes if reason provided
                    if adjustment_reason:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                        updated_notes = f"{notes}\n\n[{timestamp}] {adjustment_type}: {adjustment_amount} {unit}. {adjustment_reason}"
                        
                        conn, cursor = connect_db()
                        cursor.execute("UPDATE herbs SET notes=? WHERE id=?", (updated_notes, id))
                        conn.commit()
                        conn.close()
                    
                    # Refresh the page
                    st.rerun()
            
            # Remove Herb
            elif inventory_tab == ("Remove Herb" if lang == "ENG" else "移除藥材"):
                st.markdown("### " + ("Remove Herb from Inventory" if lang == "ENG" else "從庫存中移除藥材"))
                
                # Unpack herb data
                id, name, chinese_name, category, properties, meridians, stock_amount, unit, storage_location, date_added, expiry_date, notes, image_path = selected_herb
                
                # Show warning and confirmation
                st.warning(f"⚠️ " + (f"You are about to remove {name} ({chinese_name}) from inventory. This action cannot be undone."
                                   if lang == "ENG" else f"您即將從庫存中移除 {name} ({chinese_name})。此操作無法撤銷。"))
                
                # Show herb details
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <h4 style="margin-top: 0;">{name} ({chinese_name})</h4>
                    <p><strong>{"Category" if lang == "ENG" else "類別"}:</strong> {category}</p>
                    <p><strong>{"Stock" if lang == "ENG" else "庫存"}:</strong> {stock_amount} {unit}</p>
                    <p><strong>{"Location" if lang == "ENG" else "位置"}:</strong> {storage_location}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Confirmation checkbox
                confirm_delete = st.checkbox(("I confirm that I want to remove this herb from inventory" if lang == "ENG" 
                                           else "我確認我想從庫存中移除這種藥材"))
                
                # Delete button
                if confirm_delete:
                    if st.button("🗑️ " + ("Delete Herb" if lang == "ENG" else "刪除藥材"), use_container_width=True):
                        delete_herb(name)
                        # Refresh the page
                        st.rerun()
    
    # Inventory Report section
    elif selected_menu == "📊 Inventory Report" or selected_menu == "📊 庫存報告":
        st.subheader("📊 " + ("Inventory Report" if lang == "ENG" else "庫存報告"))
        
        # Generate report
        with st.spinner(("Generating report..." if lang == "ENG" else "生成報告中...")):
            report = generate_inventory_report()
        
        if report:
            # Overview statistics
            herbs = query_herbs()
            total_herbs = len(herbs)
            
            # Calculate total value (simplified)
            total_value = sum([herb[6] for herb in herbs])  # Sum of stock amounts
            
            # Display overview statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label=("Total Herbs" if lang == "ENG" else "藥材總數"),
                    value=total_herbs
                )
            
            with col2:
                st.metric(
                    label=("Low Stock Items" if lang == "ENG" else "低庫存項目"),
                    value=len(report['low_stock_herbs'])
                )
            
            with col3:
                st.metric(
                    label=("Expiring Soon" if lang == "ENG" else "即將過期"),
                    value=len(report['expiring_herbs'])
                )
            
            # Display category chart
            st.markdown("### " + ("Herb Distribution by Category" if lang == "ENG" else "按類別分類的藥材分佈"))
            st.image(report['category_chart'], use_column_width=True)
            
            # Display herbs expiring soon
            st.markdown("### " + ("Herbs Expiring Soon" if lang == "ENG" else "即將過期的藥材"))
            
            if report['expiring_herbs']:
                expiring_df = pd.DataFrame(report['expiring_herbs'], columns=["Name", "Expiry Date"])
                st.dataframe(expiring_df, use_container_width=True)
            else:
                st.info(("No herbs expiring soon." if lang == "ENG" else "沒有即將過期的藥材。"))
            
            # Display herbs with low stock
            st.markdown("### " + ("Herbs with Low Stock" if lang == "ENG" else "低庫存藥材"))
            
            if report['low_stock_herbs']:
                low_stock_df = pd.DataFrame(report['low_stock_herbs'], columns=["Name", "Stock Amount", "Unit"])
                st.dataframe(low_stock_df, use_container_width=True)
            else:
                st.info(("No herbs with low stock." if lang == "ENG" else "沒有低庫存的藥材。"))
            
            # Export report option
            if st.button("📄 " + ("Export Report as CSV" if lang == "ENG" else "將報告導出為CSV"), use_container_width=True):
                # Create export directory if it doesn't exist
                if not os.path.exists("exports"):
                    os.makedirs("exports")
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"exports/inventory_report_{timestamp}.csv"
                
                # Create report dataframe
                report_data = []
                
                # Add overview statistics
                report_data.append(["Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                report_data.append(["Total Herbs", total_herbs])
                report_data.append(["Low Stock Items", len(report['low_stock_herbs'])])
                report_data.append(["Expiring Soon", len(report['expiring_herbs'])])
                report_data.append([])
                
                # Add low stock herbs
                report_data.append(["Low Stock Herbs", "", ""])
                report_data.append(["Name", "Stock Amount", "Unit"])
                for herb in report['low_stock_herbs']:
                    report_data.append(herb)
                report_data.append([])
                
                # Add expiring herbs
                report_data.append(["Expiring Herbs", ""])
                report_data.append(["Name", "Expiry Date"])
                for herb in report['expiring_herbs']:
                    report_data.append(herb)
                
                # Save to CSV
                pd.DataFrame(report_data).to_csv(filename, index=False, header=False, encoding="utf-8-sig")
                
                # Create download link
                def get_csv_download_link(filename):
                    with open(filename, 'rb') as f:
                        data = f.read()
                    b64 = base64.b64encode(data).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="{os.path.basename(filename)}">Download Report</a>'
                    return href
                
                st.markdown(get_csv_download_link(filename), unsafe_allow_html=True)
        else:
            st.info(("No inventory data available to generate report." if lang == "ENG" else "沒有可用的庫存數據來生成報告。"))
    
    # Export/Import Data section
    elif selected_menu == "📤 Export/Import Data" or selected_menu == "📤 導出/導入數據":
        st.subheader("📤 " + ("Export/Import Data" if lang == "ENG" else "導出/導入數據"))
        
        # Tabs for export and import
        export_import_tab = st.radio(
            ("Select operation" if lang == "ENG" else "選擇操作"),
            [
                ("Export Data" if lang == "ENG" else "導出數據"),
                ("Import Data" if lang == "ENG" else "導入數據")
            ],
            horizontal=True
        )
        
        # Export Data
        if export_import_tab == ("Export Data" if lang == "ENG" else "導出數據"):
            st.markdown("### " + ("Export Herb Inventory Data" if lang == "ENG" else "導出藥材庫存數據"))
            
            st.markdown(("This will export all herb data to a CSV file that can be used for backup or transferring to another system."
                       if lang == "ENG" else "這將導出所有藥材數據到CSV文件，可用於備份或轉移到另一個系統。"))
            
            if st.button("📤 " + ("Export to CSV" if lang == "ENG" else "導出為CSV"), use_container_width=True):
                with st.spinner(("Exporting data..." if lang == "ENG" else "導出數據中...")):
                    export_file = export_herb_data()
                
                st.success(f"✅ " + (f"Data exported to {export_file}" if lang == "ENG" else f"數據已導出到 {export_file}"))
                
                # Create download link
                def get_csv_download_link(filename):
                    with open(filename, 'rb') as f:
                        data = f.read()
                    b64 = base64.b64encode(data).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="{os.path.basename(filename)}">Download CSV</a>'
                    return href
                
                st.markdown(get_csv_download_link(export_file), unsafe_allow_html=True)
        
        # Import Data
        else:
            st.markdown("### " + ("Import Herb Inventory Data" if lang == "ENG" else "導入藥材庫存數據"))
            
            st.markdown(("Upload a CSV file containing herb data. This will add new herbs to your inventory."
                       if lang == "ENG" else "上傳包含藥材數據的CSV文件。這將向您的庫存中添加新的藥材。"))
            
            uploaded_file = st.file_uploader(
                ("Upload CSV file" if lang == "ENG" else "上傳CSV文件"),
                type=["csv"]
            )
            
            if uploaded_file:
                # Preview the uploaded file
                df = pd.read_csv(uploaded_file)
                st.markdown("### " + ("Preview of data to import" if lang == "ENG" else "要導入的數據預覽"))
                st.dataframe(df.head(5), use_container_width=True)
                
                # Import options
                import_option = st.radio(
                    ("Import options" if lang == "ENG" else "導入選項"),
                    [
                        ("Add new herbs only" if lang == "ENG" else "僅添加新藥材"),
                        ("Update existing herbs and add new ones" if lang == "ENG" else "更新現有藥材並添加新的")
                    ]
                )
                
                # Import button
                if st.button("📥 " + ("Import Data" if lang == "ENG" else "導入數據"), use_container_width=True):
                    with st.spinner(("Importing data..." if lang == "ENG" else "導入數據中...")):
                        # Reset file pointer
                        uploaded_file.seek(0)
                        import_herb_data(uploaded_file)
                    
                    # Refresh the page
                    st.rerun()