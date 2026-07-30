import os
import pdfplumber

ALLOWED_EXTENSIONS = {"pdf", "txt"}
MAX_FILE_SIZE = 5*1024*1024
MAX_TEXT_LENGTH = 10000
MIN_TEXT_LENGTH = 50

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(file_path:str, filename: str) -> tuple[str, str | None]:
    ext = filename.rsplit(".", 1)[1].lower()

    try:
        if ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        
        elif ext == "pdf":
            text =""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text+= page_text + "\n"
            
            if not text.strip():
                return "", "No text could be extracted from this PDF"
        
        else: 
            return "", "Unsupported file type"
        
        text = text.strip()

        if len(text) < MIN_TEXT_LENGTH:
            return "", "File does not contain enough text to generate flashcards"
        
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]
        
        return text, None
    
    except Exception as e:
        return "", f"Error reading file: {str(e)}"
            

if __name__ == "__main__":
    import tempfile
    import os

    # Test 1: valid TXT file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("The SM-2 algorithm was developed by Piotr Wozniak in 1985. " * 20)
        tmp_path = f.name

    text, error = extract_text(tmp_path, "test.txt")
    print(f"✓ TXT extraction: {len(text)} characters, error={error}")
    os.remove(tmp_path)

    # Test 2: file too short
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Too short")
        tmp_path = f.name

    text, error = extract_text(tmp_path, "test.txt")
    print(f"✓ Too short: text='{text}', error='{error}'")
    os.remove(tmp_path)

    # Test 3: invalid file type
    print(f"✓ Invalid type: {allowed_file('notes.docx')} (should be False)")
    print(f"✓ Valid type:   {allowed_file('notes.pdf')} (should be True)")
    print(f"✓ Valid type:   {allowed_file('notes.txt')} (should be True)")