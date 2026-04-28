import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_email(text):
    email_regex = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    match = re.search(email_regex, text)
    return match.group(0).lower() if match else ""

def extract_phone(text):
    phone_regex = r'(?:\+?\d{1,3}[\s\-]?)?\d{5}[\s\-]?\d{5}'
    match = re.search(phone_regex, text)
    if match:
        return re.sub(r'[\s\-]', '', match.group(0))
    return ""

def generate_fallback_name(email):
    if not email:
        return "Unknown Candidate"
    local_part = email.split('@')[0]
    # Replace dots and underscores with spaces
    name_parts = re.split(r'[._-]', local_part)
    # Capitalize and join
    name = " ".join([part.capitalize() for part in name_parts if part.isalpha()])
    return name if name else "Unknown Candidate"

def extract_name(text, email):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    ignore_keywords = ["professional", "summary", "objective", "profile", "resume", "email", "phone", "contact"]
    
    def is_valid_name(line):
        if len(line) > 40:
            return False
        if any(char.isdigit() for char in line):
            return False
        if "@" in line:
            return False
        line_lower = line.lower()
        for keyword in ignore_keywords:
            if keyword in line_lower:
                return False
        words = line.split()
        if not (2 <= len(words) <= 3):
            return False
        for word in words:
            if not word[0].isupper():
                return False
            # Check if word has valid alphabetic chars
            if not word.isalpha():
                return False
        return True

    # Check first 5 lines (priority)
    for line in lines[:5]:
        if is_valid_name(line):
            return line

    # Then check up to 15 lines
    for line in lines[5:15]:
        if is_valid_name(line):
            return line

    return generate_fallback_name(email)

def extract_skills(text):
    skill_keywords = ["python", "javascript", "react", "html", "css", "sql", "ml", "django", "flask", "git"]
    text_lower = text.lower()
    # Find all words, avoiding partial matches where possible but simple keyword match is fine
    words = set(re.findall(r'\b\w+\b', text_lower))
    found_skills = [skill for skill in skill_keywords if skill in words]
    # Special cases for two-word skills if any (not in the list currently, but good to handle if added)
    return [skill.capitalize() if skill not in ['html', 'css', 'sql', 'ml'] else skill.upper() for skill in found_skills]

def detect_role(text):
    text_lower = text.lower()
    
    frontend_keywords = ['react', 'html', 'css', 'frontend', 'front-end', 'front end']
    backend_keywords = ['django', 'flask', 'node', 'backend', 'back-end', 'back end']
    data_keywords = ['sql', 'excel', 'data']
    ml_keywords = ['machine learning', 'ml', 'deep learning', 'tensorflow', 'pytorch']
    
    has_frontend = any(kw in text_lower for kw in frontend_keywords)
    has_backend = any(kw in text_lower for kw in backend_keywords)
    has_ml = any(kw in text_lower for kw in ml_keywords)
    has_data = any(kw in text_lower for kw in data_keywords)
    
    if has_frontend and has_backend:
        return "Full Stack"
    elif has_frontend:
        return "Frontend"
    elif has_backend:
        return "Backend"
    elif has_ml:
        return "ML"
    elif has_data:
        return "Data"
    
    return "Unknown Role"
