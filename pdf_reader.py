import fitz

pdf_path = "data/notes.pdf"

document = fitz.open(pdf_path)

text = ""

for page in document:
    text += page.get_text()

document.close()

print(text)