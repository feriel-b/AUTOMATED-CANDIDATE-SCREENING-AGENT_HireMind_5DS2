# In app/seed.py

from faker import Faker
import random

# Import your own project's modules
from database import SessionLocal
import models

# Initialize Faker
fake = Faker()

def seed_database():
    db = SessionLocal()
    print("Database session created.")

    try:
        # --- Clean up existing data ---
        print("Deleting existing data...")
        db.query(models.Candidate).delete()
        db.query(models.Job).delete()
        db.commit()
        print("Existing data deleted.")

        # --- Create Fake Jobs ---
        print("Creating fake jobs...")
        job_ids = []
        for _ in range(10): # Create 10 jobs
            job = models.Job(
                title=fake.job(),
                company_name=fake.company(),
                location=fake.city(),
                description=fake.paragraph(nb_sentences=10),
                required_skills=random.sample(
                    ['Python', 'React', 'SQL', 'AWS', 'Docker', 'JavaScript', 'FastAPI', 'Communication'], 
                    k=random.randint(3, 5)
                )
            )
            db.add(job)
            db.commit()
            job_ids.append(job.id)
        print(f"{len(job_ids)} jobs created.")

        # --- Create Fake Candidates ---
        print("Creating fake candidates...")
        for _ in range(30): # Create 30 candidates
            candidate = models.Candidate(
                name=fake.name(),
                email=fake.email(),
                skills=random.sample(
                    ['Python', 'React', 'SQL', 'Java', 'Project Management', 'Agile', 'C#'], 
                    k=random.randint(2, 4)
                ),
                raw_text=fake.paragraph(nb_sentences=20), # A fake resume text
                description=fake.paragraph(nb_sentences=3), # The new description field
                job_id=random.choice(job_ids), # Assign to a random job
                status=random.choice(['new', 'shortlisted', 'new']) # Make 'new' more likely
            )
            db.add(candidate)
        db.commit()
        print("30 candidates created.")

        print("Seeding complete!")

    finally:
        db.close()
        print("Database session closed.")

if __name__ == "__main__":
    seed_database()