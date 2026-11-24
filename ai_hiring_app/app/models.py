from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.types import JSON
from .database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    # Use JSON to store list of skills (works on both SQLite and Postgres)
    required_skills = Column(JSON)

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    # Use JSON to store list of candidate skills
    skills = Column(JSON)
    raw_text = Column(Text)