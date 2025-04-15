import os
import logging
import requests
from typing import Dict, List
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Language-specific system prompts
LANGUAGE_SYSTEM_PROMPTS = {
    'english': "You are a social media content creator writing in English.",
    'spanish': "Eres un creador de contenido para redes sociales escribiendo en español.",
    'french': "Vous êtes un créateur de contenu pour les réseaux sociaux écrivant en français.",
    'german': "Sie sind ein Social-Media-Content-Creator, der auf Deutsch schreibt.",
    'portuguese': "Você é um criador de conteúdo para mídias sociais escrevendo em português.",
    'italian': "Sei un creatore di contenuti per social media che scrive in italiano."
}

# Platform-specific prompt templates
PLATFORM_PROMPTS = {
    'instagram': """Convert the following transcription into an engaging Instagram caption. 
    Use relevant hashtags, keep it concise (max 2200 characters), and make it visually appealing. 
    Focus on creating a caption that will drive engagement and interest.

    Transcription: {transcription}""",

    'x': """Convert the following transcription into a sharp, concise tweet for X (Twitter). 
    Aim for maximum impact in 280 characters. Use a punchy, direct style that captures 
    the essence of the content.

    Transcription: {transcription}""",

    'linkedin': """Transform the transcription into a professional LinkedIn post. 
    Provide insights, add value, and maintain a professional tone. 
    Include key takeaways or professional learnings.

    Transcription: {transcription}""",

    'facebook': """Create a compelling Facebook post from the transcription. 
    Make it conversational, engaging, and shareable. 
    Add context and encourage interaction or discussion.

    Transcription: {transcription}"""
}

def generate_platform_content(
    transcription: str, 
    platforms: List[str] = None, 
    language: str = 'english',
    post_counts: Dict[str, int] = None
) -> Dict[str, List[str]]:
    """
    Generate content for specified social media platforms using OpenRouter API.
    
    Args:
        transcription (str): Transcribed text to convert
        platforms (List[str], optional): List of platforms to generate content for. 
                                         Defaults to all platforms.
        language (str, optional): Language for content generation. Defaults to 'english'.
        post_counts (Dict[str, int], optional): Number of posts to generate per platform.
    
    Returns:
        Dict[str, List[str]]: Generated content for each platform
    """
    # Set default platforms if not specified
    if platforms is None:
        platforms = list(PLATFORM_PROMPTS.keys())
    
    # Set default post counts if not specified
    if post_counts is None:
        post_counts = {platform: 1 for platform in platforms}
    
    # Validate platforms and language
    invalid_platforms = set(platforms) - set(PLATFORM_PROMPTS.keys())
    if invalid_platforms:
        raise ValueError(f"Invalid platforms: {invalid_platforms}")
    
    if language.lower() not in LANGUAGE_SYSTEM_PROMPTS:
        raise ValueError(f"Unsupported language: {language}. Supported languages: {list(LANGUAGE_SYSTEM_PROMPTS.keys())}")
    
    # Retrieve API key from multiple sources
    api_key = (
        os.getenv("OPENROUTER_API_KEY") or 
        os.getenv("OPENAI_API_KEY")  # Fallback to OpenAI key
    )
    
    # Debug logging for API key
    logger.info(f"API Key present: {bool(api_key)}")
    if api_key:
        logger.info(f"API Key starts with: {api_key[:5]}...")
    if not api_key:
        logger.warning("No OpenRouter API key found. Using fallback content generation.")
        return {platform: ["Content generation unavailable"] for platform in platforms}
    
    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Headers for OpenRouter API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/zpeteman/Content_Repurposer",
        "X-Title": "ContentCraft AI"
    }
    
    # Validate API key before making request
    if not api_key or len(api_key.strip()) < 10:
        logger.error("Invalid or missing API key")
        return {platform: ["Content generation unavailable - Invalid API key"] for platform in platforms}
    
    # Generate content for each platform
    platform_content = {}
    for platform in platforms:
        # Determine number of posts for this platform
        num_posts = post_counts.get(platform, 1)
        platform_posts = []
        
        for _ in range(num_posts):
            try:
                # Prepare prompt
                prompt = PLATFORM_PROMPTS[platform].format(transcription=transcription)
                
                # Prepare API payload
                payload = {
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": [
                        {"role": "system", "content": LANGUAGE_SYSTEM_PROMPTS[language.lower()]},
                        {"role": "user", "content": prompt}
                    ]
                }
                
                # Send request to OpenRouter
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                # Check response
                if response.status_code == 200:
                    # Extract generated content
                    generated_content = response.json()['choices'][0]['message']['content'].strip()
                    platform_posts.append(generated_content)
                    logger.info(f"Successfully generated content for {platform}")
                else:
                    # Log detailed error information
                    logger.error(f"Content generation failed for {platform}: {response.status_code}")
                    logger.error(f"Response text: {response.text}")
                    platform_posts.append(f"Content generation failed: {response.status_code}")
            
            except Exception as e:
                logger.error(f"Exception in content generation for {platform}: {e}")
                platform_posts.append(f"Exception generating content: {e}")
        
        platform_content[platform] = platform_posts
    
    return platform_content

def main():
    # Example usage
    sample_transcription = """
    In today's fast-paced digital world, content creation is more important than ever. 
    Creators need tools that can help them repurpose and distribute their content 
    across multiple platforms efficiently.
    """
    
    try:
        # Generate content for all platforms
        content = generate_platform_content(
            sample_transcription, 
            language='spanish',
            post_counts={'instagram': 2, 'x': 3, 'linkedin': 1, 'facebook': 2}
        )
        
        # Print generated content
        for platform, posts in content.items():
            print(f"\n--- {platform.upper()} Content ---")
            for i, post in enumerate(posts, 1):
                print(f"Post {i}:")
                print(post)
                print("-" * 50)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
