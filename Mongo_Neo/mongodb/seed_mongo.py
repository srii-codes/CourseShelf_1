"""
seed_mongo.py
Loads students.json, books.json, lending_requests.json, and lending_records.json
into the courseshelf MongoDB Atlas database.

Run this once (or again after clearing collections) to populate Atlas with the
full 50/50/35/35 sample dataset for Review 2.

Usage:
    pip install pymongo python-dotenv
    python seed_mongo.py
"""

import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # reads MONGO_URI from the .env file in this folder

client = MongoClient(os.environ["MONGO_URI"])
db = client["courseshelf"]

print("Connected to:", db.name)
print("=" * 60)

# --- Files -> collections ----------------------------------------------
FILES = {
    "students": "students.json",
    "books": "books.json",
    "lending_requests": "lending_requests.json",
    "lending_records": "lending_records.json",
}

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

for collection_name, filename in FILES.items():
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r") as f:
        documents = json.load(f)

    collection = db[collection_name]

    # Clear out any previous run of this seed script so re-running it
    # doesn't create duplicates, then insert fresh.
    deleted = collection.delete_many({}).deleted_count
    if deleted:
        print(f"Cleared {deleted} existing document(s) from '{collection_name}'")

    result = collection.insert_many(documents)
    print(f"Inserted {len(result.inserted_ids)} documents into '{collection_name}'")

print("-" * 60)
for name in FILES:
    print(f"{name}: {db[name].count_documents({})} documents now in Atlas")

client.close()
print("=" * 60)
print("Seeding complete.")