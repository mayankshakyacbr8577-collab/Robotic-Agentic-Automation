# RAG Chatbot System

A modern web-based RAG (Retrieval-Augmented Generation) chatbot for asking questions about PDF documents.

## Features

- **Modern Web Interface**: Clean, responsive UI with real-time chat
- **Improved RAG Pipeline**:
  - Better chunking with overlap for improved context
  - Optimized embeddings using SentenceTransformers
  - Enhanced prompts for more accurate answers
- **Continuous Chat**: Ready for new questions after each answer
- **Fast Vector Search**: FAISS for efficient similarity search
- **AI-Powered**: Uses Google Gemini 3.8 Flash for intelligent responses
- **Automatic Retry**: Handles API rate limits with exponential backoff

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your `.env` file contains your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

3. Place your PDF in the `data/` folder (default: `data/notes.pdf`)

## Usage

Run the application:
```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

## Improvements Made

### 1. Web Interface
- Replaced command-line interface with modern web UI
- Real-time chat with message history
- Responsive design for mobile and desktop
- Loading states and error handling

### 2. RAG Pipeline Enhancements
- **Improved Chunking**: Added overlap (100 characters) between chunks for better context preservation
- **Better Embeddings**: Using optimized SentenceTransformer model
- **Enhanced Prompts**: More specific instructions to Gemini for accurate, concise answers
- **Top-k Retrieval**: Retrieves top 5 most relevant chunks for better context

### 3. Backend Architecture
- Flask REST API for frontend-backend communication
- CORS enabled for cross-origin requests
- Health check endpoint for monitoring
- Proper error handling and logging

### 4. User Experience
- Auto-clears input after sending
- Auto-focuses input field for continuous questioning
- Visual feedback during loading
- Chat history maintained in session

## File Structure

```
RAG/
├── app.py              # Flask backend with RAG logic
├── index.html          # Frontend HTML
├── styles.css          # Frontend styling
├── script.js           # Frontend JavaScript
├── requirements.txt    # Python dependencies
├── rag.py              # Original CLI version (kept for reference)
├── pdf_reader.py       # PDF reader utility
├── .env                # Environment variables (API key)
├── .gitignore          # Git ignore rules
└── data/
    └── notes.pdf       # Your PDF document
```

## API Endpoints

- `GET /` - Serve the web interface
- `POST /api/chat` - Send a question and get an answer
- `GET /api/health` - Check system status

## Configuration

You can modify these parameters in `app.py`:

- `chunk_size`: Size of text chunks (default: 500)
- `overlap`: Overlap between chunks (default: 100)
- `k`: Number of relevant chunks to retrieve (default: 5)
- `model`: SentenceTransformer model (default: "all-MiniLM-L6-v2")
- `gemini_model`: Gemini model (default: "gemini-3.8-flash")
- `max_retries`: Maximum API retry attempts (default: 3)

## Troubleshooting

If the server doesn't start:
1. Check that all dependencies are installed
2. Verify your Google API key in `.env`
3. Ensure the PDF file exists in `data/` folder
4. Check that port 5000 is not in use

## License

MIT License
