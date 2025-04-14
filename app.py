import os
import time
import streamlit as st
import pandas as pd
from audio_download import download_youtube_audio
from transcribe import transcribe_audio
from generate_content import generate_platform_content, LANGUAGE_SYSTEM_PROMPTS

def save_uploaded_file(uploaded_file):
    """Save uploaded file to downloads directory"""
    try:
        # Create downloads directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)
        
        # Generate unique filename
        filename = os.path.join('downloads', uploaded_file.name)
        
        # Save file
        with open(filename, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return filename
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

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
    st.title("🚀 AI Content Repurposer")
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

if __name__ == "__main__":
    main()