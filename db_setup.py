from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Query
import os

# Small, plain ASCII marker so output shows even on consoles that struggle with emoji
print("START: running db_setup.py")

# Step 1: Database engine
db_path = os.path.abspath("queries.db")
print(f"Database path: {db_path}")

engine = create_engine(f"sqlite:///{db_path}")

# Step 2: Create all tables
Base.metadata.create_all(engine)
print("Tables created (if not already).")

# Step 3: Create session
Session = sessionmaker(bind=engine)
session = Session()

# Step 4: Seed data
q1 = Query(keyword="physics notes", response="Physics Notes: https://drive.google.com/drive/folders/1MQ7YfBMsy1tVSArPwLkFqX45mvdumEUn")
q2 = Query(keyword="mechanics tutorial", response="Mechanics Tutorial Sheet: https://drive.google.com/drive/folders/1vQ5XFLsAdgvK9cz70cJHjYNkYhRf5m5G")

# Check if already added
existing = session.query(Query).all()
if len(existing) == 0:
    session.add_all([q1, q2])
    session.commit()
    print("Database seeded with example queries.")
else:
    print("Data already exists, skipping seeding.")
