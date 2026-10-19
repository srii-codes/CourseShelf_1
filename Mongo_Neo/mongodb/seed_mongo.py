"""
Loads students.json, books.json, lending_requests.json and lending_records.json
into MongoDB (database from .env, default 'courseshelf').

WARNING: clears those 4 collections first (this also removes password hashes
created by auth.signup).

Usage:
    python seed_mongo.py          # asks for confirmation if data already exists
    python seed_mongo.py --yes    # no prompt
Then run:  python indexes.py
"""
import json
import os
import sys
from config import get_db

db = get_db()
print("Connected to:", db.name)

FILES = {
    "students": "students.json",
    "books": "books.json",
    "lending_requests": "lending_requests.json",
    "lending_records": "lending_records.json",
}
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

existing = {c: db[c].count_documents({}) for c in FILES}
if any(existing.values()) and "--yes" not in sys.argv:
    print("Existing data:", existing)
    if input("This will DELETE it and re-seed. Type 'yes' to continue: ").strip().lower() != "yes":
        sys.exit("Aborted, nothing changed.")

for collection_name, filename in FILES.items():
    with open(os.path.join(DATA_DIR, filename)) as f:
        documents = json.load(f)
    db[collection_name].delete_many({})
    result = db[collection_name].insert_many(documents)
    print(f"{collection_name}: inserted {len(result.inserted_ids)}")

db.counters.delete_many({})  # ID counters are rebuilt automatically from the data
print("Seeding complete. Now run: python indexes.py")
