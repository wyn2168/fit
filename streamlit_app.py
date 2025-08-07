import streamlit as st
import requests
import base64
from PIL import Image
import io
import os

# Page configuration
st.set_page_config(
    page_title="DreamFit Image-to-Image Generator",
    page_icon="👕",
    layout="wide"
)

# Title and description
st.title("👕 DreamFit Image-to-Image Generator")
st.markdown("Upload a clothing image and describe the desired style to generate a new image!")

# API endpoint - use environment variable for deployment
API_URL = os.getenv("BACKEND_API_URL", "https://f53bcc92c68b.ngrok-free.app/inference/")

def main():
    # Create two columns for input and output
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📤 Input")
        
        # File uploader for image
        uploaded_file = st.file_uploader(
            "Upload a clothing image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image of clothing you want to modify"
        )
        
        # Text input for prompt
        image_text = st.text_area(
            "Describe the desired style",
            placeholder="e.g., A woman wearing a white Bape T-shirt with a colorful ape graphic and bold text.",
            height=100,
            help="Describe how you want the clothing to look in the generated image"
        )
        
        # Seed input (optional)
        seed = st.number_input(
            "Seed (for reproducible results)",
            value=164143088151,
            help="Random seed for generation. Same seed will produce same result."
        )
        
        # Generate button
        generate_button = st.button(
            "🚀 Generate Image",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        st.header("📤 Output")
        
        # Display uploaded image
        if uploaded_file is not None:
            st.subheader("Uploaded Image")
            uploaded_image = Image.open(uploaded_file)
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
        # Generate and display results
        if generate_button and uploaded_file is not None and image_text.strip():
            with st.spinner("Generating image... This may take a few moments."):
                try:
                    # Prepare the request
                    files = {
                        "input_image": uploaded_file.getvalue()
                    }
                    data = {
                        "image_text": image_text,
                        "seed": int(seed)
                    }
                    
                    # Make API request
                    response = requests.post(API_URL, data=data, files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        encoded_images = result.get("images", [])
                        
                        if encoded_images:
                            st.success("✅ Image generated successfully!")
                            
                            # Display generated images
                            for idx, encoded_image in enumerate(encoded_images):
                                # Decode base64 image
                                image_data = base64.b64decode(encoded_image)
                                generated_image = Image.open(io.BytesIO(image_data))
                                
                                st.subheader(f"Generated Image {idx + 1}")
                                st.image(generated_image, caption=f"Generated Image {idx + 1}", use_column_width=True)
                                
                                # Download button
                                img_buffer = io.BytesIO()
                                generated_image.save(img_buffer, format="JPEG")
                                img_buffer.seek(0)
                                
                                st.download_button(
                                    label=f"📥 Download Image {idx + 1}",
                                    data=img_buffer.getvalue(),
                                    file_name=f"generated_image_{idx + 1}.jpg",
                                    mime="image/jpeg"
                                )
                        else:
                            st.error("No images were generated.")
                            
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        st.error(f"Response: {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the API server. Please make sure the FastAPI backend is running.")
                    st.info("💡 To start the backend, run: `python run_fastapi_backend.py`")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
        
        elif generate_button:
            if uploaded_file is None:
                st.warning("⚠️ Please upload an image first.")
            if not image_text.strip():
                st.warning("⚠️ Please enter a description for the desired style.")

    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ Information")
        st.markdown("""
        **How to use:**
        1. Upload a clothing image
        2. Describe the desired style
        3. Click "Generate Image"
        4. Download the result
        
        **Tips:**
        - Be specific in your description
        - Try different seeds for variety
        - The process may take 30-60 seconds
        """)
        
        st.header("🔧 API Status")
        try:
            # Use the same base URL for health check
            health_url = API_URL.replace("/inference/", "/docs")
            response = requests.get(health_url)
            if response.status_code == 200:
                st.success("✅ API is running")
            else:
                st.error("❌ API is not responding")
        except:
            st.error("❌ API is not running")
            st.info("Start the backend with: `python run_fastapi_backend.py`")

if __name__ == "__main__":
    main() 