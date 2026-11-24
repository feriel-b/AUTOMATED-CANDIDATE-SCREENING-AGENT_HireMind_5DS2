# In app/database.py

import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# --- NEW RETRY LOGIC ---
retries = 5
while retries > 0:
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        # Try to connect
        engine.connect()
        print("--- DATABASE CONNECTION SUCCESSFUL ---")
        break # Exit the loop if connection is successful
    except OperationalError as e:
        print(f"Database connection failed: {e}")
        retries -= 1
        print(f"Could not connect to database, retrying... ({retries} retries left)")
        time.sleep(5) # Wait 5 seconds before trying again
else:
    print("FATAL: Could not connect to the database after multiple retries.")
    exit(1) # Exit if we can't connect after all retries
# --- END OF NEW LOGIC ---

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()