from utils import extract_skills, extract_experience, ats_screening, calculate_similarity

# Sample Resume Text
resume_text = """
John Doe
Email: johndoe@example.com | Phone: 9876543210 | LinkedIn: linkedin.com/in/johndoe

Summary:
Experienced Machine Learning Engineer with 5+ years of experience in Python, TensorFlow, PyTorch, and NLP.

Work Experience:
- ML Engineer at XYZ Corp (2018-2023)
- Developed deep learning models for fraud detection.

Skills:
- Python, Machine Learning, Deep Learning, NLP, TensorFlow, PyTorch, SQL
"""

# Sample Job Description
job_description = """
Looking for a Machine Learning Engineer with 3+ years of experience.
Must have expertise in Python, TensorFlow, NLP, and SQL.
"""

# 🛠️ **Run Tests**
print("🟢 Extracted Skills:", extract_skills(resume_text))
print("🟢 Extracted Experience (Years):", extract_experience(resume_text))
ats_score, ats_feedback = ats_screening(resume_text)
print("🟢 ATS Score:", ats_score)
print("🟢 ATS Feedback:", ats_feedback)
match_score = calculate_similarity(resume_text, job_description, extract_skills(resume_text), extract_experience(resume_text))
print("🟢 Job Match Score:", match_score)
