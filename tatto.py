import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Initialize Stable Diffusion API key
STABLE_DIFFUSION_API_KEY = ("sk-LzV1yZBzzwz0LoH644iLvVkjzNjJ2AoD6BR7RBgyc7AtJX6j")

st.set_page_config(page_title="Tattoo Studio", layout="wide")

# --- Header ---
st.title("🎨 Tattoo Art")
st.subheader("Design your dream tattoo, explore fresh ink, and discover top UK artists.")

# --- Section 1: Create your tattoo from prompt ---
st.markdown("## ✏️ Create Your Tattoo from Prompt")

# Add style selection
style = st.selectbox(
    "Select Tattoo Style",
    ["Traditional", "Realistic", "Minimalist", "Watercolor", "Geometric", "Japanese"]
)

# Enhanced prompt input with guidance
st.markdown("""
**Tips for better results:**
- Be specific about the design elements
- Mention colors if important
- Include style preferences
- Specify placement if relevant
""")
prompt = st.text_input("Describe your dream tattoo (e.g. 'A dragon wrapped around a sword')")

if prompt:
    # Enhance the prompt with style
    enhanced_prompt = f"{prompt}, {style} style tattoo, high quality, detailed, professional tattoo design"
    
    st.info(f"🔮 Generating tattoo for: *{enhanced_prompt}*")
    
    # Show loading spinner
    with st.spinner("Generating your tattoo design..."):
        try:
            # Call Stable Diffusion API
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {STABLE_DIFFUSION_API_KEY}"
                },
                json={
                    "text_prompts": [{"text": enhanced_prompt}],
                    "cfg_scale": 7,
                    "height": 1024,
                    "width": 1024,
                    "samples": 1,
                    "steps": 30,
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                # Get the generated image
                image_data = data["artifacts"][0]["base64"]
                # Convert base64 to image
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
                st.image(image, caption="Generated Tattoo", use_column_width=True)
                
                # Add download button
                st.download_button(
                    label="Download Tattoo Design",
                    data=image_bytes,
                    file_name="tattoo_design.png",
                    mime="image/png"
                )
            else:
                st.error(f"Failed to generate tattoo. API Error: {response.text}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please check your API key and try again")

# --- Section 2: Recent Tattoos Gallery ---
st.markdown("## 🖼️ Recent Tattoos")

# Add custom CSS to enforce consistent image heights
st.markdown("""
<style>
    .gallery-image {
        height: 400px !important;
        object-fit: cover !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

cols = st.columns(3)
tattoo_image_urls = [
    "https://cdn.shopify.com/s/files/1/0162/2116/files/Wolf_tatto.jpg?v=1719483738",  # Wolf tattoo
    "https://cdn.shopify.com/s/files/1/0162/2116/files/t8shwd3c51311.jpg?v=1719484070",  # Bird tattoo
    "https://cdn.shopify.com/s/files/1/0162/2116/files/Screen_Shot_2024-06-27_at_3.55.21_PM.png?v=1719483944",  # Nature-themed tattoo
]

for col, url in zip(cols, tattoo_image_urls):
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        
        # Display image with fixed height using custom CSS class
        col.markdown(f'<img src="{url}" class="gallery-image">', unsafe_allow_html=True)
    except Exception as e:
        col.warning("⚠️ Could not load image.")
        col.text(str(e))

# --- Section 3: UK Tattoo Business Listings (Imaginary Data) ---
st.markdown("## 🏪 UK Tattoo Studios")

businesses = [
    {
        "name": "Ink Haven",
        "location": "Camden Town, London",
        "rating": "4.9 ⭐",
        "desc": "Specialists in minimalist and fine-line tattoos. Walk-ins welcome."
    },
    {
        "name": "The Black Needle",
        "location": "Northern Quarter, Manchester",
        "rating": "4.7 ⭐",
        "desc": "Award-winning realism artists with custom design services."
    },
    {
        "name": "Eternal Mark Studio",
        "location": "Brighton Seafront",
        "rating": "4.8 ⭐",
        "desc": "Beachside studio known for vibrant colors and sleeve work."
    }
]

for biz in businesses:
    st.markdown(f"**{biz['name']}**  \n📍 {biz['location']}  \n⭐ {biz['rating']}  \n_{biz['desc']}_")
    st.markdown("---")
