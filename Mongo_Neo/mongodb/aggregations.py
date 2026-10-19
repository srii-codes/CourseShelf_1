from config import get_db, today_str

db = get_db()
print("Connected to:", db.name)
print("=" * 60)

# ---------- 1. Most-requested books ----------
print("1. MOST REQUESTED BOOKS (top 5 by number of lending_requests)")
pipeline1 = [
    {"$group": {"_id": "$book_id", "request_count": {"$sum": 1}}},
    {"$sort": {"request_count": -1, "_id": 1}},
    {"$limit": 5},
    {"$lookup": {"from": "books", "localField": "_id", "foreignField": "book_id", "as": "book"}},
    {"$unwind": "$book"},
    {"$project": {"_id": 0, "book_id": "$_id", "title": "$book.title",
                  "edition": "$book.edition", "request_count": 1}},
]
for doc in db.lending_requests.aggregate(pipeline1):
    print(" ", doc)
print("-" * 60)

# ---------- 2. Books per department (via owner's department) ----------
print("2. BOOKS COUNT PER DEPARTMENT")
pipeline2 = [
    {"$lookup": {"from": "students", "localField": "owner_id",
                 "foreignField": "student_id", "as": "owner_info"}},
    {"$unwind": "$owner_info"},
    {"$group": {"_id": "$owner_info.department", "book_count": {"$sum": 1}}},
    {"$sort": {"book_count": -1}},
]
for doc in db.books.aggregate(pipeline2):
    print(" ", doc)
print("-" * 60)

# ---------- 3. Average lending duration (in days) ----------
print("3. AVERAGE LENDING DURATION (days, returned loans only)")
pipeline3 = [
    {"$match": {"returned_on": {"$ne": None}}},
    {"$project": {"duration_days": {"$divide": [
        {"$subtract": [{"$dateFromString": {"dateString": "$returned_on"}},
                       {"$dateFromString": {"dateString": "$borrowed_on"}}]},
        1000 * 60 * 60 * 24]}}},
    {"$group": {"_id": None, "avg_duration_days": {"$avg": "$duration_days"},
                "loans_counted": {"$sum": 1}}},
]
for doc in db.lending_records.aggregate(pipeline3):
    print(" ", doc)
print("-" * 60)

# ---------- 4. Currently overdue books ----------
print("4. CURRENTLY OVERDUE BOOKS (due_date passed, not yet returned)")
pipeline4 = [
    {"$match": {"returned_on": None, "due_date": {"$lt": today_str()}}},
    {"$count": "overdue_count"},
]
result = list(db.lending_records.aggregate(pipeline4))
print(" ", result if result else [{"overdue_count": 0}])
print("-" * 60)

# ---------- 5. High-demand / low-supply titles ----------
print("5. HIGH-DEMAND / LOW-SUPPLY TITLES (pending requests exceed available copies)")
pipeline5 = [
    {"$lookup": {"from": "lending_requests", "localField": "book_id",
                 "foreignField": "book_id", "as": "requests"}},
    {"$group": {
        "_id": "$title",
        "total_copies": {"$sum": 1},
        "available_copies": {"$sum": {"$cond": [{"$eq": ["$status", "available"]}, 1, 0]}},
        "pending_requests": {"$sum": {"$size": {"$filter": {
            "input": "$requests", "as": "r",
            "cond": {"$eq": ["$$r.status", "pending"]}}}}},
    }},
    {"$match": {"$expr": {"$gt": ["$pending_requests", "$available_copies"]}}},
    {"$sort": {"pending_requests": -1, "_id": 1}},
]
found = False
for doc in db.books.aggregate(pipeline5):
    found = True
    print(" ", doc)
if not found:
    print("  (no title currently has more pending requests than available copies)")
print("-" * 60)
print("All aggregation queries completed.")
