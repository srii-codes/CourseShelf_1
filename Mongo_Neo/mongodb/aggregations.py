from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # reads MONGO_URI from the .env file in this folder

client = MongoClient(os.environ["MONGO_URI"])
db = client["courseshelf"]

print("Connected to:", db.name)
print("=" * 60)

# ---------- 1. Most-requested books ----------
print("1. MOST REQUESTED BOOKS (by number of lending_requests)")
pipeline1 = [
    {"$group": {"_id": "$book_id", "request_count": {"$sum": 1}}},
    {"$sort": {"request_count": -1}},
    {"$limit": 5}
]
for doc in db.lending_requests.aggregate(pipeline1):
    print(" ", doc)
print("-" * 60)

# ---------- 2. Books per department (via owner's department) ----------
print("2. BOOKS COUNT PER DEPARTMENT")
pipeline2 = [
    {"$lookup": {
        "from": "students",
        "localField": "owner_id",
        "foreignField": "student_id",
        "as": "owner_info"
    }},
    {"$unwind": "$owner_info"},
    {"$group": {"_id": "$owner_info.department", "book_count": {"$sum": 1}}},
    {"$sort": {"book_count": -1}}
]
for doc in db.books.aggregate(pipeline2):
    print(" ", doc)
print("-" * 60)

# ---------- 3. Average lending duration (in days) ----------
print("3. AVERAGE LENDING DURATION (days, for records with a return date)")
pipeline3 = [
    {"$match": {"returned_on": {"$ne": None}}},
    {"$project": {
        "duration_days": {
            "$divide": [
                {"$subtract": [
                    {"$dateFromString": {"dateString": "$returned_on"}},
                    {"$dateFromString": {"dateString": "$borrowed_on"}}
                ]},
                1000 * 60 * 60 * 24
            ]
        }
    }},
    {"$group": {"_id": None, "avg_duration_days": {"$avg": "$duration_days"}}}
]
for doc in db.lending_records.aggregate(pipeline3):
    print(" ", doc)
print("-" * 60)

# ---------- 4. Count of currently overdue books ----------
print("4. CURRENTLY OVERDUE BOOKS (due_date passed, not yet returned)")
from datetime import datetime
today = datetime.utcnow().strftime("%Y-%m-%d")
pipeline4 = [
    {"$match": {
        "returned_on": None,
        "due_date": {"$lt": today}
    }},
    {"$count": "overdue_count"}
]
result = list(db.lending_records.aggregate(pipeline4))
print(" ", result if result else [{"overdue_count": 0}])
print("-" * 60)

# ---------- 5. High-demand, low-supply books (circulation visibility) ----------
print("5. HIGH-DEMAND / LOW-SUPPLY BOOKS (requests exceed available copies of that title)")
pipeline5 = [
    {"$lookup": {
        "from": "lending_requests",
        "localField": "book_id",
        "foreignField": "book_id",
        "as": "requests"
    }},
    {"$group": {
        "_id": "$title",
        "total_copies": {"$sum": 1},
        "available_copies": {"$sum": {"$cond": [{"$eq": ["$status", "available"]}, 1, 0]}},
        "total_requests": {"$sum": {"$size": "$requests"}}
    }},
    {"$match": {"$expr": {"$gt": ["$total_requests", "$available_copies"]}}},
    {"$sort": {"total_requests": -1}}
]
for doc in db.books.aggregate(pipeline5):
    print(" ", doc)
print("-" * 60)

client.close()
print("All aggregation queries completed.")