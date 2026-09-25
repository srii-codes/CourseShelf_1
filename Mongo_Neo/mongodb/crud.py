from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # reads MONGO_URI from the .env file in this folder

# Connect to your database
client = MongoClient(os.environ["MONGO_URI"])
db = client["courseshelf"]

print("Connected to:", db.name)
print("-" * 50)

# ---------- CREATE ----------
new_student = {
    "student_id": "S051",
    "name": "Kavya Reddy",
    "department": "CSE",
    "courses_enrolled": ["CSE301", "CSE303"],
    "contact": "kavya.reddy@vitstudent.ac.in"
}
result = db.students.insert_one(new_student)
print("CREATE: Inserted new student with _id:", result.inserted_id)

new_book = {
    "book_id": "B051",
    "title": "Artificial Intelligence",
    "edition": "3rd",
    "condition": "Good",
    "owner_id": "S051",
    "status": "available"
}
result = db.books.insert_one(new_book)
print("CREATE: Inserted new book with _id:", result.inserted_id)
print("-" * 50)

# ---------- READ ----------
print("READ: Books owned by S002:")
for book in db.books.find({"owner_id": "S002"}):
    print(" -", book["title"], "|", book["edition"])

print("\nREAD: Student S001 details:")
student = db.students.find_one({"student_id": "S001"})
print(" ", student)
print("-" * 50)

# ---------- UPDATE ----------
result = db.books.update_one(
    {"book_id": "B001"},
    {"$set": {"status": "lent_out"}}
)
print("UPDATE: Modified", result.modified_count, "document(s) — B001 status set to 'lent_out'")

result = db.lending_requests.update_one(
    {"request_id": "R001"},
    {"$set": {"status": "accepted"}}
)
print("UPDATE: Modified", result.modified_count, "document(s) — R001 status set to 'accepted'")
print("-" * 50)

# ---------- DELETE ----------
# Delete one completed lending record (has a returned_on date, not null)
completed_record = db.lending_records.find_one({"returned_on": {"$ne": None}})
if completed_record:
    result = db.lending_records.delete_one({"_id": completed_record["_id"]})
    print("DELETE: Removed", result.deleted_count, "completed lending record — record_id:", completed_record.get("record_id"))
else:
    print("DELETE: No completed record found to delete")

client.close()
print("-" * 50)
print("All CRUD operations completed.")