from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Boolean
import os
import json  # Import JSON for handling lists
from passlib.context import CryptContext

# Database Configuration
DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///./resume_matcher.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

# Resume Model
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    skills = Column(Text)  # Store skills as JSON text
    experience_years = Column(Float)
    match_score = Column(Float)
    job_ranking = Column(Float)
    ats_score = Column(Float)
    ats_feedback = Column(String)
    job_description = Column(Text)

    # Convert skills list to JSON before storing
    def set_skills(self, skills_list):
        self.skills = json.dumps(skills_list)

    # Convert JSON string back to list when retrieving
    def get_skills(self):
        return json.loads(self.skills) if self.skills else []

# Feedback Model
class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    rating = Column(Float)
    comments = Column(String)

# Create Tables
Base.metadata.create_all(bind=engine)
