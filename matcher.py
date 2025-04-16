import pdfplumber
import docx
import re
import spacy
import fitz  # PyMuPDF
import nltk
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

# Load NLP Model
nlp = spacy.load("en_core_web_sm")

# Load Pre-trained BERT Model
bert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Download stopwords (only needed once)
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# Expanded Skill Database
SKILL_DATABASE = {
    "python", "java", "c++", "javascript", "typescript", "react", "node.js", "sql",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "html", "css",
    "flask", "django", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "git",
    "bash", "agile", "scrum", "data science", "pandas", "numpy", "matplotlib", "fastapi",
    "microservices", "mongodb", "postgresql", "graphql", "llm", "bert", "transformers"
}

# Function to Extract Text from PDF
def extract_text_from_pdf(pdf_path):
    """
    Extract text from a resume PDF.
    - Uses PyMuPDF for normal PDFs.
    - Uses pdfplumber for scanned PDFs.
    """
    text = ""

    try:
        with fitz.open(pdf_path) as doc:
            text = " ".join([page.get_text("text") for page in doc])
    except Exception as e:
        print(f"PyMuPDF error: {e}")

    if not text.strip():
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        except Exception as e:
            print(f"pdfplumber error: {e}")

    return text.strip() if text else "No text found."

# Function to Extract Text from DOCX
def extract_text_from_docx(docx_path):
    return "\n".join([para.text for para in docx.Document(docx_path).paragraphs])

# Function to Extract Skills using NLP
def extract_skills(resume_text):
    """
    Extracts skills from the resume text using NLP (spaCy + NLTK).
    """
    doc = nlp(resume_text)
    skills = {token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"] and token.text.lower() in SKILL_DATABASE}
    
    return list(skills)

# Function to Extract Keywords
def extract_keywords(text, top_n=10):
    """
    Extracts the most frequent keywords (excluding stopwords).
    """
    words = re.findall(r"\b\w+\b", text.lower())
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    return Counter(filtered_words).most_common(top_n)

# Function to Optimize Resume for ATS
def optimize_resume_for_ats(text):
    """
    Ensures the resume follows ATS-friendly guidelines:
    - Removes special characters.
    - Converts to plain text.
    - Checks if essential sections exist.
    """
    text = re.sub(r"[^a-zA-Z0-9\s.,]", "", text)

    required_sections = {"experience", "skills", "education", "projects"}
    missing_sections = {section for section in required_sections if section.lower() not in text.lower()}

    return {"optimized_text": text, "missing_sections": list(missing_sections)}

# Function to Calculate Resume Match Score (TF-IDF + BERT)
def match_resume_with_job(resume_text, job_description):
    """
    Calculates the resume-job match score using:
    - TF-IDF for lexical similarity.
    - BERT for semantic similarity.
    - Skill match weight.
    """

    # TF-IDF Cosine Similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    tfidf_similarity = cosine_similarity(tfidf_matrix)[0][1]

    # BERT Semantic Similarity
    embeddings = bert_model.encode([resume_text, job_description])
    bert_similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()

    # Extract skills from resume
    extracted_skills = extract_skills(resume_text)
    skill_match_count = sum(1 for skill in extracted_skills if skill in job_description.lower())
    skill_weight = (skill_match_count / len(extracted_skills)) if extracted_skills else 0

    # Weighted Score Calculation
    final_score = (0.5 * tfidf_similarity) + (0.4 * bert_similarity) + (0.1 * skill_weight)
    
    return round(final_score * 100, 2)  # Convert to percentage

# Function to Recommend Jobs
def recommend_jobs(resume_text, job_descriptions):
    """
    Matches the resume to a list of job descriptions using semantic similarity.
    Returns top 3 job recommendations.
    """
    job_scores = [(job, match_resume_with_job(resume_text, job)) for job in job_descriptions]
    return sorted(job_scores, key=lambda x: x[1], reverse=True)[:3]  # Return top 3 matches
