import os
import logging
import streamlit as st
import yt_dlp
import ffmpeg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_youtube_url(url: str) -> bool:
    """
    Validate if the provided URL is a valid YouTube URL.
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    return url.startswith(('https://www.youtube.com/', 'https://youtu.be/'))

def download_youtube_audio(url, output_dir='downloads'):
    """
    Download audio from YouTube URL using yt-dlp with enhanced error handling
    
    Args:
        url (str): YouTube video URL
        output_dir (str): Directory to save downloaded audio
    
    Returns:
        str: Path to downloaded audio file
    """
    # Validate URL
    if not validate_youtube_url(url):
        raise ValueError("Invalid YouTube URL. Please provide a valid YouTube video link.")
    
    # Ensure downloads directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Enhanced yt-dlp options for better compatibility
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
        'progress_hooks': [_download_progress],
        
        # Enhanced bot protection bypass
        'cookiefile': None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'add_headers': {
            'Referer': 'https://www.youtube.com/',
            'Origin': 'https://www.youtube.com'
        }
    }
    
    try:
        # Use context manager for safer resource handling
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video information first
            info_dict = ydl.extract_info(url, download=False)
            
            # Validate video availability
            if not info_dict:
                raise ValueError("Unable to extract video information")
            
            # Perform download
            result = ydl.download([url])
            
            # Find the downloaded file
            for file in os.listdir(output_dir):
                if file.endswith('.mp3'):
                    audio_path = os.path.join(output_dir, file)
                    
                    # Validate file size
                    if os.path.getsize(audio_path) > 0:
                        logger.info(f"Successfully downloaded audio: {audio_path}")
                        return audio_path
            
            raise FileNotFoundError("No audio file was downloaded")
    
    except Exception as e:
        error_message = f"Error downloading audio: {str(e)}"
        logger.error(error_message)
        st.error(error_message)
        raise

def _download_progress(d):
    """
    Track download progress
    
    Args:
        d (dict): Download progress information
    """
    if d['status'] == 'finished':
        st.toast('Download complete, converting...', icon='✅')
    elif d['status'] == 'downloading':
        downloaded_bytes = d.get('downloaded_bytes', 0)
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        
        if total_bytes > 0:
            progress = (downloaded_bytes / total_bytes) * 100
            st.progress(progress / 100)

def convert_to_mp3(input_file, output_dir='downloads'):
    """
    Convert audio file to MP3 using FFmpeg
    
    Args:
        input_file (str): Path to input audio file
        output_dir (str): Directory to save converted file
    
    Returns:
        str: Path to converted MP3 file
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        filename = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_dir, f"{filename}.mp3")
        
        # Convert using FFmpeg
        (
            ffmpeg
            .input(input_file)
            .output(output_file, acodec='libmp3lame', audio_bitrate='192k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        # Remove original file
        os.remove(input_file)
        
        logger.info(f"Successfully converted to MP3: {output_file}")
        return output_file
    
    except ffmpeg.Error as e:
        error_message = f"FFmpeg conversion error: {e.stderr.decode()}"
        logger.error(error_message)
        st.error(error_message)
        raise
    except Exception as e:
        error_message = f"Unexpected error during conversion: {str(e)}"
        logger.error(error_message)
        st.error(error_message)
        raise

def main():
    # Example usage with error handling
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
    
    try:
        url = input("Enter YouTube URL or local file path: ")
        if validate_youtube_url(url):
            audio_path = download_youtube_audio(url)
            print(f"Audio downloaded to: {audio_path}")
        else:
            # Local file conversion
            try:
                # Get file extension
                file_ext = os.path.splitext(url)[1].lower()
                
                # If it's already an audio file, just return the path
                if file_ext in ['.mp3', '.wav', '.ogg', '.flac']:
                    print(f"File is already an audio file: {url}")
                else:
                    # For video files, convert to mp3
                    output_path = convert_to_mp3(url)
                    print(f"File converted to MP3: {output_path}")
            
            except Exception as e:
                print(f"Error processing local file: {e}")
    
    except ValueError as ve:
        print(f"URL Error: {ve}")
    except RuntimeError as re:
        print(f"Download Error: {re}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
