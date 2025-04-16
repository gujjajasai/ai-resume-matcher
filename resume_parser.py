import pytesseract
from pdf2image import convert_from_path
import spacy
import re
import cv2
import numpy as np
import logging
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from fuzzywuzzy import process
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load NLP model
nlp = spacy.load("en_core_web_sm")
bert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Skill Database with fuzzy matching
SKILL_DATABASE = [
    "python", "java", "c++", "javascript", "typescript", "react", "node.js", "sql",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "flask",
    "django", "fastapi", "docker", "aws", "azure", "gcp", "linux", "git",
    "data science", "pandas", "numpy", "matplotlib", "keras", "cv", "llm", "mlops"
]

def preprocess_image(image):
    """
    Converts an image to grayscale and applies adaptive thresholding for better OCR accuracy.
    """
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF using OCR.
    """
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            processed_img = preprocess_image(img)
            text += pytesseract.image_to_string(processed_img, config='--psm 6') + "\n"
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
    return text.strip()

def extract_skills(text):
    """
    Extracts relevant skills from text using fuzzy matching and NLP.
    """
    doc = nlp(text.lower())
    extracted_skills = set()
    
    for token in doc:
        best_match, score = process.extractOne(token.text, SKILL_DATABASE)
        if score > 80:  # High-confidence match
            extracted_skills.add(best_match)
    
    return list(extracted_skills)

def extract_experience(text):
    """
    Extracts years of experience from resume text using regex.
    """
    experience_patterns = [
        r"(\d+)\s*(?:\+?\s*years?|yrs?|y)\s*(?:of\s*experience)?",
        r"(\d+)\s*-\s*(\d+)\s*years?",
        r"(\d+)\s*-\s*(present|current)",
        r"(\d+)\s*(?:years?|yrs?)\s*plus"
    ]
    years = []
    for pattern in experience_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                if isinstance(match, tuple):
                    start_year = int(match[0])
                    end_year = datetime.now().year if match[1].lower() in ("present", "current") else int(match[1])
                    years.append(end_year - start_year)
                else:
                    years.append(int(match))
            except ValueError:
                continue
    return max(years) if years else 0

def ats_screening(resume_text):
    """
    Checks ATS compatibility using keyword density (TF-IDF) instead of regex.
    """
    required_sections = ["contact", "education", "experience", "skills"]
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform([resume_text])
    keywords_found = sum(1 for word in required_sections if word in tfidf.get_feature_names_out())
    ats_score = (keywords_found / len(required_sections)) * 100
    return round(ats_score, 2), "ATS-friendly" if ats_score > 70 else "Missing key sections"

def calculate_similarity(resume_text, job_description, skills, experience):
    """
    Computes similarity using BERT embeddings and TF-IDF weighting.
    """
    embeddings = bert_model.encode([resume_text, job_description])
    similarity_score = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    
    # TF-IDF Similarity
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform([resume_text, job_description])
    tfidf_similarity = (tfidf_matrix * tfidf_matrix.T).toarray()[0, 1]
    
    # Skill matching
    skill_match_count = sum(1 for skill in skills if skill in job_description.lower())
    skill_weight = (skill_match_count / len(skills)) if skills else 0
    
    # Experience weight
    exp_weight = 0.3 if experience >= 3 else 0.15
    
    # Final weighted score
    final_score = (0.5 * similarity_score) + (0.3 * skill_weight) + (0.2 * tfidf_similarity) + (0.1 * exp_weight)
    return round(final_score * 100, 2)

def parse_resume(pdf_path, job_description):
    """
    Parses a resume PDF and evaluates it against a job description.
    """
    text = extract_text_from_pdf(pdf_path)
    skills = extract_skills(text)
    experience = extract_experience(text)
    ats_score, ats_feedback = ats_screening(text)
    match_score = calculate_similarity(text, job_description, skills, experience)
    
    return {
        "raw_text": text,
        "skills": skills,
        "experience": experience,
        "ats_score": ats_score,
        "ats_feedback": ats_feedback,
        "match_score": match_score
    }
