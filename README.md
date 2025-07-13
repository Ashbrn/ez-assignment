# 🧠 Smart Assistant for Research Summarization

An intelligent document analysis tool that helps you summarize, chat with, and test your understanding of PDF and TXT documents using AI.

## ✨ Features

- **📄 Document Upload**: Support for PDF and TXT files
- **📑 Smart Summarization**: Generate concise summaries (≤150 words)
- **💬 Interactive Chat**: Ask questions about your document with conversation history
- **🧠 Challenge Mode**: Test your knowledge with:
  - Multiple Choice Questions (MCQ)
  - Open-ended analytical questions
  - Mixed mode (MCQ + Open questions)

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Groq API key

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your Groq API key:**
   - Get your free API key from [Groq Console](https://console.groq.com/)
   - Create a `.env` file in the project root:
     ```
     GROQ_API_KEY=your_api_key_here
     ```

3. **Run the application:**
   
   **Option 1 - Simple Python script (Recommended):**
   ```bash
   python start_app.py
   ```
   
   **Option 2 - Auto-restart monitor (For stability):**
   ```bash
   python keep_alive.py
   ```
   
   **Option 3 - Direct Streamlit:**
   ```bash
   streamlit run app.py
   ```
   
   **Option 4 - Windows Batch file:**
   ```bash
   run_app.bat
   ```

4. **Open your browser** and go to `http://localhost:8501`

5. **To stop the application:**
   - Press `Ctrl+C` in the terminal, or
   - Run: `python stop_app.py`

## 📖 How to Use

1. **Upload Document**: Use the sidebar to upload a PDF or TXT file
2. **Choose Mode**:
   - **Summary**: Get a concise overview of your document
   - **Ask Anything**: Chat with AI about the document content
   - **Challenge Me**: Test your understanding with AI-generated questions

### Challenge Mode Options:
- **Mixed (MCQ + Open)**: 2 multiple choice + 1 analytical question
- **Multiple Choice Only**: 3 MCQ questions with instant feedback
- **Open-ended Only**: 3 analytical questions requiring detailed answers

## 🛠️ Project Structure

```
smart-assistant/
├── app.py              # Main Streamlit application
├── utils.py            # Document processing and question generation
├── groq_api.py         # Groq API integration
├── requirements.txt    # Python dependencies
├── run_app.bat        # Windows batch file to run the app
└── README.md          # This file
```

## 🔧 Configuration

The app uses environment variables for configuration:
- `GROQ_API_KEY`: Your Groq API key (required)
- `GROQ_MODEL`: AI model to use (default: llama-3.1-70b-versatile)

## 📝 Supported File Types

- **PDF**: Automatically extracts text content
- **TXT**: Direct text file processing

## 🤖 AI Features

- **Smart Question Generation**: Creates document-specific questions using extracted facts
- **Conversation Memory**: Maintains chat history during your session
- **Instant Feedback**: Real-time scoring for multiple choice questions
- **Detailed Evaluation**: AI assessment for open-ended answers

## 🎯 Tips for Best Results

1. **Upload clear, well-structured documents** for better question generation
2. **Use specific questions** in chat mode for more accurate responses
3. **Try different challenge modes** to test various aspects of understanding
4. **Review explanations** in MCQ mode to learn from mistakes

## 🔍 Troubleshooting

- **Connection Error**: Make sure your Groq API key is valid and you have internet connection
- **Poor Question Quality**: Try uploading documents with more specific facts, numbers, and clear concepts
- **Slow Response**: The AI model processing may take a few seconds, especially for longer documents
- **App Stops Automatically**: This can happen due to:
  - Network timeouts - restart the app with `python start_app.py`
  - Memory issues - try smaller documents
  - Port conflicts - use `python stop_app.py` then restart
  - For maximum stability, use `python keep_alive.py`
- **Port Already in Use**: Run `python stop_app.py` to stop existing processes, then restart

## 🔧 Stability Features

- **Auto-retry**: API calls automatically retry with different models if one fails
- **Connection monitoring**: App shows real-time API connection status
- **Auto-restart**: Use `keep_alive.py` for automatic restart if the app crashes
- **Error recovery**: Graceful handling of network issues and timeouts

---

**Enjoy learning with your Smart Assistant! 🚀📚**