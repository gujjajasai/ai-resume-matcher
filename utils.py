import spacy
from sentence_transformers import SentenceTransformer, util
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from spacy.matcher import PhraseMatcher

# Load NLP model
nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab)

# Pre-trained BERT model
bert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Expanded Skill Database
SKILL_DATABASE = [
    "python", "java", "c++", "c#", "javascript", "typescript", "react", "node.js",
    "sql", "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "html", "css", "flask", "django", "fastapi", "docker", "kubernetes",
    "aws", "azure", "gcp", "linux", "git", "bash", "agile", "scrum",
    "data science", "pandas", "numpy", "matplotlib", "mlops", "cv", "llm"
]

# Preload skill patterns
skill_patterns = [nlp(skill) for skill in SKILL_DATABASE]
matcher.add("SKILLS", None, *skill_patterns)

def extract_skills(text):
    """Extracts skills using phrase matching."""
    doc = nlp(text.lower())
    matches = matcher(doc)
    extracted_skills = set([doc[start:end].text for match_id, start, end in matches])
    return list(extracted_skills)

def extract_experience(text):
    """Extracts years of experience from text."""
    experience_patterns = [
        r"(\d+)\s*(?:\+?\s*years?|yrs|y)\s*(?:of\s*experience)?",  
        r"(\d+)\s*-\s*(\d+)\s*years?",  
        r"since\s*(\d{4})"  # Example: "since 2015"
    ]

    years = []
    for pattern in experience_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):  
                years.append((int(match[0]) + int(match[1])) // 2)
            elif match.isdigit():
                years.append(2025 - int(match))  # Assuming current year is 2025
            else:
                years.append(int(match))

    return max(years) if years else 0

def calculate_similarity(resume_text, job_description, extracted_skills, experience_years):
    """Computes weighted similarity between a resume and job description."""
    embeddings = bert_model.encode([resume_text, job_description])
    similarity_score = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform([resume_text, job_description])
    tfidf_similarity = (tfidf_matrix * tfidf_matrix.T).toarray()[0, 1]

    skill_match_count = sum(1 for skill in extracted_skills if skill in job_description.lower())
    skill_weight = (skill_match_count / len(extracted_skills)) if extracted_skills else 0

    exp_weight = min(experience_years / 10, 1) * 0.2  # Scale experience impact

    final_score = (0.5 * similarity_score) + (0.3 * skill_weight) + (0.2 * tfidf_similarity) + (0.1 * exp_weight)
    return round(final_score * 100, 2)

def ats_screening(resume_text):
    """Checks ATS compatibility based on formatting, keyword density, and structure."""
    ats_criteria = {
        "contact information": r"(phone|email|linkedin|github)",
        "education": r"(bachelor|master|phd|degree|university|college)",
        "experience": r"(experience|worked at|position|years)",
        "skills": r"(skills|technologies|expertise)",
        "keywords": r"(python|java|ml|data science|tensorflow|react|aws|sql)",
        "no images": r"(jpg|png|gif|image)",
        "proper formatting": r"(pdf|docx)",
        "bullet points": r"•|\d+\.\s",  # Checks for bullet points
    }

    missing_criteria = [key for key, pattern in ats_criteria.items() if not re.search(pattern, resume_text, re.IGNORECASE)]
    ats_score = ((len(ats_criteria) - len(missing_criteria)) / len(ats_criteria)) * 100
    ats_feedback = "Missing: " + ", ".join(missing_criteria) if missing_criteria else "Resume is ATS-friendly."

    return round(ats_score, 2), ats_feedback

def semantic_search(resume_text, job_description):
    """Ranks resumes against job descriptions using semantic similarity."""
    embeddings = bert_model.encode([resume_text, job_description])
    ranking_score = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item() * 100
    return round(ranking_score, 2)
