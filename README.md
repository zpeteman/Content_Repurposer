# 🚀 AI Content Repurposer

## 📝 Overview

AI Content Repurposer is an innovative, open-source tool designed to transform video and audio content into engaging, multi-platform social media posts. Leveraging cutting-edge AI technologies, this application helps content creators maximize their reach by generating platform-specific content effortlessly.

## ✨ Features

- 🎥 **Universal Content Extraction**
  - Download audio from various video/audio URLs
  - Upload local audio and video files
  - Supports multiple file formats

- 🔊 **Advanced Transcription**
  - Uses OpenAI Whisper for accurate audio transcription
  - Handles multiple languages and accents

- 🌐 **Multi-Platform Content Generation**
  - Generate content for Instagram, X (Twitter), LinkedIn, Facebook
  - Customize number of posts per platform
  - Choose content language (English, Spanish, French, German, and more)

- 🤖 **AI-Powered Content Creation**
  - Utilizes advanced language models
  - Adapts content style to each social media platform
  - Maintains context and key message

## 🛠 Tech Stack

- **Frontend**: Streamlit
- **Transcription**: OpenAI Whisper
- **Content Generation**: OpenRouter AI
- **Language**: Python 3.8+

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg
- OpenRouter API Key

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ai-content-repurposer.git
   cd ai-content-repurposer
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

4. Run the application
   ```bash
   streamlit run app.py
   ```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛣 Roadmap

- [ ] Add more language support
- [ ] Implement custom tone and style settings
- [ ] Create browser extension
- [ ] Add image generation capabilities
- [ ] Develop analytics for generated content

## 💡 Support

If you encounter any issues or have questions, please file an issue on our GitHub repository.

---

**Disclaimer**: This tool is for educational and creative purposes. Always respect copyright and content creator rights.
