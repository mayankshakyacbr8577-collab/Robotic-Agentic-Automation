import warnings
warnings.filterwarnings("ignore")

import pymupdf
from sentence_transformers import SentenceTransformer
import faiss
from google import genai
from dotenv import load_dotenv
import os


# =========================================================
# 1. LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file.")
    exit()

client = genai.Client(api_key=api_key)


# =========================================================
# 2. READ PDF
# =========================================================

pdf_path = "data/notes.pdf"

document = pymupdf.open(pdf_path)

text = ""

for page in document:
    text += page.get_text()

document.close()


# =========================================================
# 3. SPLIT PDF INTO CHUNKS
# =========================================================

chunk_size = 500

chunks = []

for i in range(0, len(text), chunk_size):

    chunk = text[i:i + chunk_size]

    if chunk.strip():
        chunks.append(chunk)


print("PDF loaded successfully!")
print("Total chunks:", len(chunks))


# =========================================================
# 4. CREATE EMBEDDINGS
# =========================================================

print("\nLoading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(
    chunks,
    convert_to_numpy=True
)

print("Embeddings created successfully!")


# =========================================================
# 5. CREATE FAISS DATABASE
# =========================================================

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

print("FAISS database ready!")
print("Total vectors:", index.ntotal)


# =========================================================
# 6. START CHATBOT
# =========================================================

print("\n========================================")
print("          PDF RAG CHATBOT")
print("========================================")

print("Ask questions about your PDF.")
print("Type 'exit' to close the chatbot.")
print("========================================\n")


# =========================================================
# 7. CHAT LOOP
# =========================================================

while True:

    question = input("Question: ").strip()


    # -----------------------------------------------------
    # Exit chatbot
    # -----------------------------------------------------

    if question.lower() == "exit":

        print("\nGoodbye Mayank! 👋")
        break


    # -----------------------------------------------------
    # Empty question check
    # -----------------------------------------------------

    if not question:

        print("Please enter a question.\n")
        continue


    # =====================================================
    # 8. CONVERT QUESTION INTO EMBEDDING
    # =====================================================

    question_embedding = model.encode(
        [question],
        convert_to_numpy=True
    )


    # =====================================================
    # 9. SEARCH FAISS
    # =====================================================

    k = min(5, len(chunks))

    distances, indices = index.search(
        question_embedding,
        k
    )


    # =====================================================
    # 10. GET RELEVANT PDF CHUNKS
    # =====================================================

    relevant_chunks = []

    for i in indices[0]:

        if i >= 0:
            relevant_chunks.append(chunks[i])


    context = "\n\n".join(relevant_chunks)


    # =====================================================
    # 11. ASK GEMINI
    # =====================================================

    response = client.models.generate_content(

        model="gemini-3.8-flash",

        contents=f"""
You are a professional PDF question-answering assistant.

The user's name is Mayank Shakya.
IMPORTANT RULES:
1. Always start your answer with:
   "Mayank Shakya,"
2. Answer ONLY from the provided PDF context.
3. Keep the answer short and clear.
4. Use bullet points when listing multiple things.
5. Give a maximum of 3-5 bullet points.
6. Do not repeat the user's question.
7. Do not give unnecessary explanations.
8. Do not provide information that is not present
   in the PDF context.
9. If the answer cannot be found in the PDF context,
   say:
   "Mayank Shakya, I could not find this information
   in the provided PDF."

10. Do not make up information.


==============================
PDF CONTEXT
==============================

{context}


==============================
USER QUESTION
==============================

{question}

Now provide a short and accurate answer.
"""
    )


    # =====================================================
    # 12. DISPLAY ANSWER
    # =====================================================

    print("\nAI 🤖:")

    print(response.text)

    print("\n----------------------------------------\n")