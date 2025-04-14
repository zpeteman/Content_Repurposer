import os
import time
import streamlit as st
import pandas as pd
from audio_download import download_youtube_audio
from transcribe import transcribe_audio
from generate_content import generate_platform_content, LANGUAGE_SYSTEM_PROMPTS

# Retrieve secrets with fallback values
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
WHISPER_MODEL = st.secrets.get("WHISPER_MODEL", "base")
DOWNLOAD_DIR = st.secrets.get("DOWNLOAD_DIR", "downloads/")
MAX_FILE_SIZE_MB = st.secrets.get("MAX_FILE_SIZE_MB", 50)
SUPPORTED_LANGUAGES = st.secrets.get("SUPPORTED_LANGUAGES", 
    ["english", "spanish", "french", "german", "portuguese", "italian"])

# Page configuration before any other Streamlit commands
st.set_page_config(
    page_title="ContentCraft AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check for API key early
if not OPENROUTER_API_KEY:
    st.error("""
    ## 🔑 API Key Required
    
    To use ContentCraft AI, you need to:
    
    1. Obtain an OpenRouter API Key from [OpenRouter](https://openrouter.ai/)
    2. Configure the key in your Streamlit app's secrets
    
    #### How to Set Up:
    - Go to Streamlit Cloud
    - Navigate to your app's settings
    - Add a secret named `OPENROUTER_API_KEY` with your API key
    
    [Learn more about Streamlit secrets](https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app/connect-to-external-resources)
    """)
    st.stop()

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to downloads directory"""
    try:
        # Generate unique filename
        filename = os.path.join(DOWNLOAD_DIR, uploaded_file.name)
        
        # Save file
        with open(filename, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return filename
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def cleanup_audio_file(audio_path):
    """
    Safely delete the audio file after processing
    
    Args:
        audio_path (str): Path to the audio file to be deleted
    """
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            st.toast(f"Temporary audio file {os.path.basename(audio_path)} deleted successfully", icon="🗑️")
    except Exception as e:
        st.warning(f"Could not delete audio file: {e}")

def main():
    # Custom CSS for better UI
    st.markdown("""
    <style>
    .main-container {
        display: flex;
        flex-direction: row;
    }
    .sidebar {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-right: 20px;
    }
    .content-area {
        flex-grow: 1;
    }
    .platform-bar {
        background-color: #e6e6e6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # App title and description
    st.title("🚀 ContentCraft AI")
    st.markdown("Transform your content across multiple social media platforms")

    # Sidebar for platform selection and options
    with st.sidebar:
        st.header("🔧 Content Settings")
        
        # Input source selection
        input_source = st.radio("Choose Input Source", 
                                ["Video/Audio URL", "Upload File"], 
                                index=0)
        
        # Language selection
        language = st.selectbox(
            "Select Content Language", 
            list(LANGUAGE_SYSTEM_PROMPTS.keys()),
            index=0
        )
        
        # Platform selection and post count configuration
        st.subheader("Platform Content Configuration")
        
        # Create a dataframe for platform post counts
        platforms = ["instagram", "x", "linkedin", "facebook"]
        df = pd.DataFrame({
            'Platform': platforms,
            'Number of Posts': [1] * len(platforms)
        })
        
        # Editable dataframe for post counts
        edited_df = st.data_editor(
            df, 
            column_config={
                "Number of Posts": st.column_config.NumberColumn(
                    "Number of Posts",
                    help="How many posts to generate for each platform",
                    min_value=0,
                    max_value=5,
                    step=1
                )
            },
            hide_index=True,
            key="platform_posts"
        )

    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Input based on selected source
        if input_source == "Video/Audio URL":
            video_url = st.text_input("Enter Video/Audio URL", placeholder="https://example.com/video")
            input_source_value = video_url
        else:
            uploaded_file = st.file_uploader("Upload Audio/Video File", 
                                             type=['mp3', 'wav', 'mp4', 'avi', 'mov'])
            input_source_value = uploaded_file

        # Process button
        process_button = st.button("Generate Content")

    # Progress and result display
    if process_button:
        if not input_source_value:
            st.warning("Please provide a valid input")
            return

        audio_path = None
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Step 1: Download/Save File
            status_text.text("Step 1: Preparing File...")
            progress_bar.progress(10)
            time.sleep(0.5)

            if input_source == "Video/Audio URL":
                audio_path = download_youtube_audio(input_source_value)
            else:
                audio_path = save_uploaded_file(input_source_value)

            # Step 2: Transcribe
            status_text.text("Step 2: Transcribing Audio...")
            progress_bar.progress(40)
            time.sleep(0.5)
            transcription = transcribe_audio(audio_path)

            # Step 3: Generate Content
            status_text.text("Step 3: Generating Platform Content...")
            progress_bar.progress(70)
            time.sleep(0.5)
            
            # Convert edited dataframe to dictionary for post counts
            post_counts = dict(zip(edited_df['Platform'], edited_df['Number of Posts']))
            
            platform_content = generate_platform_content(
                transcription['text'], 
                platforms=list(post_counts.keys()),
                language=language,
                post_counts=post_counts
            )

            # Step 4: Display Results
            status_text.text("Content Generated Successfully!")
            progress_bar.progress(100)

            # Display platform content in expandable sections
            st.subheader("🌐 Generated Platform Content")
            for platform, posts in platform_content.items():
                with st.expander(f"{platform.upper()} Content"):
                    for i, post in enumerate(posts, 1):
                        st.text_area(f"{platform.capitalize()} Post {i}", post, key=f"{platform}_{i}")
                        st.button(f"Copy {platform.capitalize()} Post {i}", 
                                  key=f"copy_{platform}_{i}", 
                                  on_click=lambda p=platform, c=post: 
                                  st.clipboard.copy(c))

        except Exception as e:
            st.error(f"An error occurred: {e}")
            progress_bar.progress(0)
            status_text.text("Error: Process Failed")
        
        finally:
            # Always attempt to clean up audio file
            if audio_path:
                cleanup_audio_file(audio_path)

if __name__ == "__main__":
    main()