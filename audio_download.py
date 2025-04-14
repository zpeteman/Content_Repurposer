import os
import logging
from typing import Optional
import yt_dlp
import subprocess

def validate_youtube_url(url: str) -> bool:
    """
    Validate if the provided URL is a valid YouTube URL.
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    return url.startswith(('https://www.youtube.com/', 'https://youtu.be/'))

def download_youtube_audio(url: str, output_path: Optional[str] = None) -> str:
    """
    Download audio from a YouTube URL or convert a video file to audio.
    
    Args:
        url (str): YouTube URL or local file path
        output_path (Optional[str]): Directory to save audio file. Defaults to 'downloads/'
    
    Returns:
        str: Path to the downloaded/converted audio file
    
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If audio download fails
    """
    # Validate URL
    if not (validate_youtube_url(url) or os.path.exists(url)):
        raise ValueError("Invalid YouTube URL or file path. Please provide a valid YouTube video link or a local file path.")
    
    # Set default output path if not provided
    if output_path is None:
        output_path = os.path.join(os.getcwd(), 'downloads')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Check if it's a local file or YouTube URL
    if url.startswith(('http://', 'https://', 'www.')):
        # YouTube URL download
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                audio_path = ydl.prepare_filename(info_dict)
                
                # Change extension to mp3
                audio_path = os.path.splitext(audio_path)[0] + '.mp3'
                
                logging.info(f"Successfully downloaded audio: {audio_path}")
                return audio_path
        
        except Exception as e:
            logging.error(f"Error downloading YouTube audio: {e}")
            raise
    
    else:
        # Local file conversion
        try:
            # Get file extension
            file_ext = os.path.splitext(url)[1].lower()
            
            # If it's already an audio file, just return the path
            if file_ext in ['.mp3', '.wav', '.ogg', '.flac']:
                return url
            
            # For video files, convert to mp3
            output_path = os.path.join(output_path, f"{os.path.splitext(os.path.basename(url))[0]}.mp3")
            
            # Use ffmpeg to convert video to audio
            subprocess.run([
                'ffmpeg', 
                '-i', url, 
                '-vn',  # Ignore video
                '-acodec', 'libmp3lame',  # Use MP3 codec
                '-q:a', '2',  # Best quality
                output_path
            ], check=True)
            
            logging.info(f"Successfully converted to audio: {output_path}")
            return output_path
        
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg conversion error: {e}")
            raise RuntimeError(f"Failed to convert file: {e}")
        except Exception as e:
            logging.error(f"Error processing local file: {e}")
            raise

def main():
    # Example usage with error handling
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
    
    try:
        url = input("Enter YouTube URL or local file path: ")
        audio_path = download_youtube_audio(url)
        print(f"Audio downloaded to: {audio_path}")
    except ValueError as ve:
        print(f"URL Error: {ve}")
    except RuntimeError as re:
        print(f"Download Error: {re}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
