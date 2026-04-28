from flask import Blueprint, request, jsonify

from backend.utils.extract import extract_text_from_pdf, extract_email, extract_phone, extract_name, extract_skills, detect_role

from backend.utils.scoring import calculate_score, get_missing_skills, generate_ai_summary, get_decision, get_experience_keywords
analyze_bp = Blueprint('analyze_bp', __name__)

@analyze_bp.route('/api/analyze', methods=['POST'])
def analyze_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    try:
        pdf_bytes = file.read()
        text = extract_text_from_pdf(pdf_bytes)
        
        if not text:
            return jsonify({"error": "Could not extract text from PDF"}), 400
            
        email = extract_email(text)
        phone = extract_phone(text)
        name = extract_name(text, email)
        skills = extract_skills(text)
        role = detect_role(text)
        score = calculate_score(text, skills)
        missing_skills, suggestions = get_missing_skills(skills, text)
        ai_summary = generate_ai_summary(role, skills, score, text)
        decision = get_decision(score)
        experience_keywords = get_experience_keywords(text)
        
        return jsonify({
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
        return jsonify({"error": str(e)}), 500
