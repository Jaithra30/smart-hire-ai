import re
from flask import Blueprint, request, jsonify
from utils.extract import extract_text_from_pdf, extract_email, extract_phone, extract_name, extract_skills, detect_role
from utils.scoring import calculate_score, get_missing_skills, generate_ai_summary, get_decision, get_experience_keywords

hr_bp = Blueprint('hr_bp', __name__)

def split_text_into_candidates(text):
    lines = text.split('\n')
    email_regex = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    
    candidate_start_indices = []
    for i, line in enumerate(lines):
        if re.search(email_regex, line):
            start_idx = max(0, i - 3)
            if candidate_start_indices and start_idx <= candidate_start_indices[-1]:
                if i - candidate_start_indices[-1] < 10:
                    continue
                start_idx = candidate_start_indices[-1] + 1
            candidate_start_indices.append(start_idx)
            
    if not candidate_start_indices:
        return [text]
        
    candidate_start_indices[0] = 0
    chunks = []
    for i in range(len(candidate_start_indices)):
        start = candidate_start_indices[i]
        end = candidate_start_indices[i+1] if i+1 < len(candidate_start_indices) else len(lines)
        chunks.append('\n'.join(lines[start:end]))
        
    return chunks

@hr_bp.route('/api/hr-upload', methods=['POST'])
def hr_upload():
    if 'files' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
        
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files selected"}), 400
        
    if len(files) > 10:
        return jsonify({"error": "Maximum 10 files allowed"}), 400

    candidates = []
    seen_emails = set()
    seen_name_phone = set()
    
    for file in files:
        try:
            pdf_bytes = file.read()
            text = extract_text_from_pdf(pdf_bytes)
            if not text:
                continue
                
            chunks = split_text_into_candidates(text)
            
            for chunk in chunks:
                email = extract_email(chunk)
                phone = extract_phone(chunk)
                name = extract_name(chunk, email)
                skills = extract_skills(chunk)
                role = detect_role(chunk)
                score = calculate_score(chunk, skills)
                missing_skills, suggestions = get_missing_skills(skills, chunk)
                ai_summary = generate_ai_summary(role, skills, score, chunk)
                decision = get_decision(score)
                experience_keywords = get_experience_keywords(chunk)
                
                # Duplicate check
                is_duplicate = False
                normalized_email = email.lower() if email else ""
                normalized_phone = phone.replace(" ", "").replace("-", "") if phone else ""
                normalized_name = name.strip().lower() if name else ""
                
                if normalized_email:
                    if normalized_email in seen_emails:
                        is_duplicate = True
                    else:
                        seen_emails.add(normalized_email)
                else:
                    name_phone_key = f"{normalized_name}_{normalized_phone}"
                    if name_phone_key in seen_name_phone:
                        is_duplicate = True
                    else:
                        seen_name_phone.add(name_phone_key)
                        
                if not is_duplicate:
                    candidates.append({
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "skills": skills,
                        "role": role,
                        "score": score,
                        "missing_skills": missing_skills,
                        "suggestions": suggestions,
                        "ai_summary": ai_summary,
                        "decision": decision,
                        "experience_keywords": experience_keywords
                    })
                    
        except Exception as e:
            print(f"Error processing file {file.filename}: {e}")
            continue

    # Sort candidates by score descending
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Return max 10 candidates
    return jsonify({"candidates": candidates[:10]})
