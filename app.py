import warnings
warnings.filterwarnings("ignore")

import pymupdf
from sentence_transformers import SentenceTransformer
import faiss
from google import genai
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file.")
    exit()

client = genai.Client(api_key=api_key)

# =========================================================
# INITIALIZE FLASK APP
# =========================================================

app = Flask(__name__)
CORS(app)

# =========================================================
# GLOBAL VARIABLES FOR RAG
# =========================================================

chunks = []
index = None
model = None

# =========================================================
# IMPROVED CHUNKING WITH OVERLAP
# =========================================================

def improved_chunking(text, chunk_size=500, overlap=100):
    """Split text into overlapping chunks for better context"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk.strip():
            chunks.append(chunk.strip())
        
        start = end - overlap  # Overlap for better context
    
    return chunks

# =========================================================
# LOAD PDF AND INITIALIZE RAG
# =========================================================

def initialize_rag():
    global chunks, index, model
    
    print("Loading PDF...")
    pdf_path = "data/notes.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF file not found at {pdf_path}")
        return False
    
    document = pymupdf.open(pdf_path)
    text = ""
    
    for page in document:
        text += page.get_text()
    
    document.close()
    
    # Improved chunking with overlap
    chunks = improved_chunking(text, chunk_size=500, overlap=100)
    
    print(f"PDF loaded successfully! Total chunks: {len(chunks)}")
    
    # Load embedding model
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Create embeddings
    embeddings = model.encode(chunks, convert_to_numpy=True)
    
    print("Embeddings created successfully!")
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    print("FAISS database ready! Total vectors:", index.ntotal)
    return True

# =========================================================
# API ENDPOINT: GET ANSWER
# =========================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    global chunks, index, model
    
    data = request.json
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': 'Please enter a question'}), 400
    
    if not chunks or not index or not model:
        return jsonify({'error': 'RAG system not initialized'}), 500
    
    try:
        print(f"\n=== Processing Question ===")
        print(f"Question: {question}")
        
        # Convert question to embedding
        print("Creating question embedding...")
        question_embedding = model.encode([question], convert_to_numpy=True)
        
        # Search FAISS
        print("Searching FAISS index...")
        k = min(5, len(chunks))
        distances, indices = index.search(question_embedding, k)
        print(f"Found {len(indices[0])} relevant chunks")
        
        # Get relevant chunks
        relevant_chunks = []
        for i in indices[0]:
            if i >= 0 and i < len(chunks):
                relevant_chunks.append(chunks[i])
        
        context = "\n\n".join(relevant_chunks)
        print(f"Context length: {len(context)} characters")
        
        # Improved prompt for better answers with retry logic
        print("Calling Gemini API...")
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=f"""You are a professional PDF question-answering assistant for Mayank Shakya.

STRICT RULES:
1. Start your answer with: "Mayank Shakya,"
2. Answer ONLY from the provided PDF context below
3. Keep answers concise and clear (2-4 sentences maximum)
4. Use bullet points only when listing multiple items
5. Maximum 3-5 bullet points if needed
6. Never repeat the user's question
7. Never add unnecessary explanations
8. Never provide information not in the PDF context
9. If answer is not in the PDF, say: "Mayank Shakya, I could not find this information in the provided PDF."
10. Never make up information

==============================
PDF CONTEXT
==============================
{context}

==============================
USER QUESTION
==============================
{question}

Provide a short, accurate answer based ONLY on the PDF context above."""
                )
                
                print("Response received successfully")
                print(f"Answer length: {len(response.text)} characters")
                
                return jsonify({
                    'answer': response.text,
                    'chunks_used': len(relevant_chunks)
                })
                
            except Exception as api_error:
                error_str = str(api_error)
                if "503" in error_str or "UNAVAILABLE" in error_str:
                    if attempt < max_retries - 1:
                        print(f"API busy (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay} seconds...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        raise api_error
                else:
                    raise api_error
    
    except Exception as e:
        import traceback
        print(f"\n=== ERROR OCCURRED ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Full traceback:")
        traceback.print_exc()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# =========================================================
# SERVE FRONTEND
# =========================================================

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# =========================================================
# HEALTH CHECK
# =========================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'chunks_loaded': len(chunks),
        'vectors_in_index': index.ntotal if index else 0
    })

# =========================================================
# MAIN
# =========================================================

if __name__ == '__main__':
    if initialize_rag():
        print("\n" + "="*50)
        print("RAG System Initialized Successfully!")
        print("="*50)
        print("\nStarting Flask server...")
        print("Open http://localhost:5000 in your browser\n")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to initialize RAG system")
