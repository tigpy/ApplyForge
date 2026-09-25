"""
Standalone DB Seeder Script for ApplyForge
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.domain.database import init_db, SessionLocal
from packages.documents.seed_data import seed_database

if __name__ == "__main__":
    print("Initializing Database & Seeding Master Candidate Profile (Aryan Singh)...")
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
        print("Database seeding completed successfully.")
    finally:
        db.close()
