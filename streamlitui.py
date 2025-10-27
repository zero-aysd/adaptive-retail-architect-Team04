import streamlit as st
import requests
import base64
from typing import List

# === Config ===
API_URL = "http://localhost:8000/generate_layout"  # Change if deployed

st.set_page_config(page_title="Retail Layout Generator", layout="centered")
st.title("AI Retail Layout Generator")

st.markdown("""
Generate adaptive retail store layouts using AI.  
Enter a city and target products → get a 2D layout instantly.
""")

# === Input Form ===
with st.form("layout_form"):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        city = st.text_input("City", value="Surat", help="e.g., Mumbai, Delhi, Bangalore")
    
    with col2:
        keywords_input = st.text_input(
            "Keywords (comma-separated)", 
            value="iPhone 15, gaming laptop",
            help="Products to optimize layout for"
        )
    
    submitted = st.form_submit_button("Generate Layout", use_container_width=True)

# === Generate & Display ===
if submitted:
    if not city.strip():
        st.error("Please enter a city.")
    else:
        keywords: List[str] = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        with st.spinner("Generating layout with AI..."):
            try:
                payload = {
                    "city": city,
                    "keywords": keywords if keywords else None
                }
                
                response = requests.post(API_URL, json=payload, timeout=120)
                
                if response.status_code != 200:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                else:
                    data = response.json()
                    base64_str = data["diagram_base64"]
                    
                    # Render image
                    img_bytes = base64.b64decode(base64_str)
                    st.image(img_bytes, caption=f"Layout for {city} | Products: {', '.join(keywords)}", use_column_width=True)
                    
                    # Optional: Download button
                    st.download_button(
                        label="Download Diagram (PNG)",
                        data=img_bytes,
                        file_name=f"layout_{city.lower()}.png",
                        mime="image/png"
                    )
            
            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Is the FastAPI server running?")
            except Exception as e:
                st.error(f"Unexpected error: {e}")