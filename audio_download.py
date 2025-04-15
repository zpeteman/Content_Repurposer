import os
import logging
import streamlit as st
import yt_dlp
import ffmpeg
from urllib.parse import urlparse
from pytube import YouTube

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """
    Check if the provided URL is valid
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def download_audio_file(url, output_dir='downloads'):
    """
    Download audio from various platforms
    
    Args:
        url (str): URL of the video/audio
        output_dir (str): Directory to save downloaded audio
    
    Returns:
        str: Path to downloaded audio file
    """
    # Validate URL
    if not is_valid_url(url):
        raise ValueError("Invalid URL. Please provide a valid video or audio link.")
    
    # Ensure downloads directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # yt-dlp options for audio download
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'no_warnings': True,
        'ignoreerrors': False,
        'nooverwrites': True,
        'no_color': True,
        'verbose': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video information
            info_dict = ydl.extract_info(url, download=True)
            
            # Get the audio filename
            audio_filename = ydl.prepare_filename(info_dict)
            audio_path = os.path.splitext(audio_filename)[0] + '.mp3'
            
            # Validate file
            if not os.path.exists(audio_path):
                raise FileNotFoundError("Audio file not found after download")
            
            if os.path.getsize(audio_path) == 0:
                raise ValueError("Downloaded audio file is empty")
            
            logger.info(f"Successfully downloaded audio: {audio_path}")
            return audio_path
    
    except Exception as e:
        error_message = f"Error downloading audio: {str(e)}"
        logger.error(error_message)
        st.error(error_message)
        raise

def main():
    """
    Example usage of audio download function
    """
    try:
        url = input("Enter video/audio URL: ")
        audio_path = download_audio_file(url)
        print(f"Audio downloaded to: {audio_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
