import os
import logging
import whisper

def transcribe_audio(audio_path: str, model_size: str = 'base') -> dict:
    """
    Transcribe audio file using OpenAI's Whisper model.
    
    Args:
        audio_path (str): Path to the audio file to transcribe
        model_size (str, optional): Size of Whisper model. Defaults to 'base'.
    
    Returns:
        dict: Transcription result with text and other metadata
    """
    # Validate audio file
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        # Load Whisper model
        logging.info(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        # Transcribe audio
        logging.info(f"Transcribing audio: {audio_path}")
        result = model.transcribe(audio_path, fp16=False)
        
        return result
    
    except Exception as e:
        logging.error(f"Transcription error: {e}")
        raise RuntimeError(f"Failed to transcribe audio: {e}")
