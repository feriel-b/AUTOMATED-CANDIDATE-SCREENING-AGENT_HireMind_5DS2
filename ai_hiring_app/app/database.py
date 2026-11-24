from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

"""
Database configuration
----------------------
Defaults to a local SQLite database when DATABASE_URL is not provided.
This allows running the API without Docker/Postgres during local development.

Supported DATABASE_URL examples:
- Postgres: postgresql+psycopg2://user:password@localhost:5432/dbname
- SQLite (file): sqlite:///./app.db
- SQLite (memory): sqlite:///:memory:
"""

# Read from env; fallback to SQLite file for local runs
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./app.db"

# If using SQLite, include check_same_thread=False
engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)

# Each instance of the SessionLocal class will be a new database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our ORM models will inherit from
Base = declarative_base()

# Dependency to get a DB session in our API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()