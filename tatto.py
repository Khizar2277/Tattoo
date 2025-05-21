import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
from dotenv import load_dotenv
import base64
import numpy as np

# Load environment variables
load_dotenv()

# Initialize Stable Diffusion API key
STABLE_DIFFUSION_API_KEY = ("sk-LzV1yZBzzwz0LoH644iLvVkjzNjJ2AoD6BR7RBgyc7AtJX6j")

# Cache the generated tattoo
@st.cache_data
def generate_tattoo(prompt, style, size_dimensions):
    enhanced_prompt = f"{prompt}, {style} style tattoo, high quality, detailed, professional tattoo design"
    
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
            "height": size_dimensions[1],
            "width": size_dimensions[0],
            "samples": 1,
            "steps": 30,
        },
    )
    
    if response.status_code == 200:
        data = response.json()
        image_data = data["artifacts"][0]["base64"]
        image_bytes = base64.b64decode(image_data)
        return Image.open(BytesIO(image_bytes)), image_bytes
    else:
        raise Exception(f"API Error: {response.text}")

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

# Add size selection
tattoo_size = st.selectbox(
    "Select Tattoo Size",
    ["Small", "Medium", "Large"],
    index=0  # Default to Small
)

# Map size to dimensions (using allowed SDXL dimensions)
size_dimensions = {
    "Small": (768, 1344),  # Portrait orientation
    "Medium": (1024, 1024),  # Square
    "Large": (1536, 640)  # Landscape orientation
}

# Enhanced prompt input with guidance
st.markdown("""
**Tips for better results:**
- Be specific about the design elements
- Mention colors if important
- Include style preferences
- Specify placement if relevant
""")
prompt = st.text_input("Describe your dream tattoo (e.g. 'A dragon wrapped around a sword')")

# Add image upload for tattoo preview
st.markdown("## 🖼️ Preview Tattoo on Your Image")
uploaded_file = st.file_uploader("Upload an image to see how the tattoo would look", type=['png', 'jpg', 'jpeg'])

if prompt:
    st.info(f"🔮 Generating tattoo for: *{prompt}*")
    
    # Show loading spinner
    with st.spinner("Generating your tattoo design..."):
        try:
            # Generate tattoo using cached function
            tattoo_image, image_bytes = generate_tattoo(prompt, style, size_dimensions[tattoo_size])
            
            # Create two columns for side-by-side display
            col1, col2 = st.columns(2)
            
            # Display the generated tattoo in first column
            with col1:
                st.markdown("### Generated Tattoo")
                st.image(tattoo_image, use_container_width=True)
                # Add download button for the tattoo
                st.download_button(
                    label="Download Tattoo Design",
                    data=image_bytes,
                    file_name="tattoo_design.png",
                    mime="image/png"
                )
            
            # If user uploaded an image, show the preview in second column
            if uploaded_file is not None:
                with col2:
                    st.markdown("### Tattoo Preview")
                    # Load the uploaded image
                    body_image = Image.open(uploaded_file)
                    
                    # Add controls for tattoo placement
                    st.markdown("#### Adjust Tattoo Placement")
                    
                    # Size control
                    size_percentage = st.slider(
                        "Tattoo Size (%)",
                        min_value=10,
                        max_value=50,
                        value=25,
                        help="Adjust the size of the tattoo relative to the image"
                    )
                    
                    # Position controls
                    col_x, col_y = st.columns(2)
                    with col_x:
                        x_position = st.slider(
                            "Horizontal Position",
                            min_value=0,
                            max_value=100,
                            value=50,
                            help="Move tattoo left/right"
                        )
                    with col_y:
                        y_position = st.slider(
                            "Vertical Position",
                            min_value=0,
                            max_value=100,
                            value=50,
                            help="Move tattoo up/down"
                        )
                    
                    # Rotation control
                    rotation = st.slider(
                        "Rotation (degrees)",
                        min_value=-180,
                        max_value=180,
                        value=0,
                        help="Rotate the tattoo"
                    )
                    
                    # Opacity control
                    opacity = st.slider(
                        "Opacity (%)",
                        min_value=20,
                        max_value=100,
                        value=100,
                        help="Adjust how visible the tattoo is"
                    )
                    
                    # Create a copy of the original tattoo for manipulation
                    current_tattoo = tattoo_image.copy()
                    
                    # Resize tattoo based on percentage
                    max_size = min(body_image.size) * (size_percentage / 100)
                    current_tattoo.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    
                    # Create a copy of the body image for the preview
                    preview_image = body_image.copy()
                    
                    # Convert images to RGBA if they aren't already
                    if preview_image.mode != 'RGBA':
                        preview_image = preview_image.convert('RGBA')
                    if current_tattoo.mode != 'RGBA':
                        current_tattoo = current_tattoo.convert('RGBA')
                    
                    # Rotate the tattoo
                    current_tattoo = current_tattoo.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
                    
                    # Create a new transparent image for the tattoo
                    tattoo_overlay = Image.new('RGBA', preview_image.size, (0, 0, 0, 0))
                    
                    # Calculate position based on sliders
                    x = int((preview_image.width - current_tattoo.width) * (x_position / 100))
                    y = int((preview_image.height - current_tattoo.height) * (y_position / 100))
                    
                    # Apply opacity
                    if opacity < 100:
                        # Convert opacity to alpha value (0-255)
                        alpha = int(255 * (opacity / 100))
                        # Create a new image with adjusted opacity
                        current_tattoo.putalpha(alpha)
                    
                    # Paste the tattoo onto the overlay
                    tattoo_overlay.paste(current_tattoo, (x, y), current_tattoo)
                    
                    # Blend the images
                    preview_image = Image.alpha_composite(preview_image, tattoo_overlay)
                    
                    # Display the preview
                    st.image(preview_image, use_container_width=True)
                    
                    # Add download button for the preview
                    buffered = BytesIO()
                    preview_image.save(buffered, format="PNG")
                    st.download_button(
                        label="Download Preview",
                        data=buffered.getvalue(),
                        file_name="tattoo_preview.png",
                        mime="image/png"
                    )
            else:
                with col2:
                    st.info("Upload an image to see the tattoo preview")
                    
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
