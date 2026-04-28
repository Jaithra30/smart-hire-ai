def calculate_score(text, skills):
    score = 0
    text_lower = text.lower()
    
    # 1. Skill Match Score (up to 50 points)
    skill_score = min(len(skills) * 5, 50)
    score += skill_score
    
    # Bonus for multiple skills
    if len(skills) >= 5:
        score += 10
        
    # 2. Keywords Match Score (up to 40 points)
    keywords = {
        'project': 10,
        'internship': 10,
        'developed': 10,
        'built': 10
    }
    
    for kw, points in keywords.items():
        if kw in text_lower:
            score += points
            
    return min(score, 100)

def get_missing_skills(skills, text):
    all_skills = ["Python", "JavaScript", "React", "HTML", "CSS", "SQL", "ML", "Django", "Flask", "Git"]
    skills_lower = [s.lower() for s in skills]
    missing = []
    for s in all_skills:
        if s.lower() not in skills_lower:
            missing.append(s)
            
    top_missing = missing[:3]
    suggestions = []
    
    for s in top_missing:
        if s in ["React", "Django", "Flask"]:
            suggestions.append(f"Build more projects using {s}")
        elif s in ["JavaScript", "Python"]:
            suggestions.append(f"Improve {s} foundational knowledge")
        else:
            suggestions.append(f"Gain practical experience with {s}")
            
    text_lower = text.lower()
    if 'internship' not in text_lower and 'experience' not in text_lower:
        suggestions.append("Gain internship or work experience")
        
    return top_missing, list(dict.fromkeys(suggestions))[:3]

def generate_ai_summary(role, skills, score, text):
    text_lower = text.lower()
    has_project = 'project' in text_lower
    has_internship = 'internship' in text_lower
    
    summary = f"This candidate fits the profile of a {role} professional. "
    if skills:
        summary += f"They show proficiency in {', '.join(skills)}. "
    else:
        summary += "Their resume lacks common technical skill keywords. "
        
    if has_internship:
        summary += "They possess valuable internship experience, indicating prior professional exposure. "
    if has_project:
        summary += "They have hands-on experience developing projects, demonstrating practical application of skills. "
        
    if score >= 75:
        summary += "Overall, a very strong candidate with a great mix of skills and practical experience."
    elif score >= 50:
        summary += "Overall, a decent candidate with potential, though they may require some ramp-up time or further skill development."
    else:
        summary += "Their profile currently appears somewhat thin on technical keywords and verifiable experience."
        
    return summary

def get_decision(score):
    if score >= 75:
        return "Hire"
    elif score >= 50:
        return "Consider"
    else:
        return "Not Recommended"

def get_experience_keywords(text):
    text_lower = text.lower()
    found = []
    if 'project' in text_lower: found.append('project')
    if 'internship' in text_lower: found.append('internship')
    return found
