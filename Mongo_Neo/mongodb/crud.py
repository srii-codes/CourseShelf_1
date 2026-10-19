"""
CRUD demo for the report/viva. Works ONLY on temporary DEMO documents
(ids S900 / B900 / R900 / L900) and removes them at the end, so your real
data is never changed. Safe to run any number of times.
"""
from config import get_db

db = get_db()
print("Connected to:", db.name)
print("-" * 50)


def cleanup():
    db.students.delete_many({"student_id": "S900"})
    db.books.delete_many({"book_id": "B900"})
    db.lending_requests.delete_many({"request_id": "R900"})
    db.lending_records.delete_many({"record_id": "L900"})


cleanup()  # in case a previous run was interrupted
try:
    # ---------- CREATE ----------
    db.students.insert_one({"student_id": "S900", "name": "Demo Student", "department": "CSE",
                            "courses_enrolled": ["CSE301"], "contact": "demo@example.com"})
    db.books.insert_one({"book_id": "B900", "title": "Artificial Intelligence", "edition": "3rd",
                         "condition": "Good", "owner_id": "S900", "status": "available"})
    db.lending_requests.insert_one({"request_id": "R900", "book_id": "B900",
                                    "requester_id": "S001", "status": "pending",
                                    "requested_on": "2026-01-01"})
    db.lending_records.insert_one({"record_id": "L900", "request_id": "R900", "book_id": "B900",
                                   "lender_id": "S900", "borrower_id": "S001",
                                   "borrowed_on": "2026-01-02", "due_date": "2026-01-16",
                                   "returned_on": "2026-01-10"})
    print("CREATE: inserted demo student, book, request and loan record")
    print("-" * 50)

    # ---------- READ ----------
    print("READ: books owned by S900:")
    for book in db.books.find({"owner_id": "S900"}, {"_id": 0}):
        print(" -", book["title"], "|", book["edition"])
    print("READ: student S001:", db.students.find_one({"student_id": "S001"}, {"_id": 0, "password_hash": 0}))
    print("-" * 50)

    # ---------- UPDATE ----------
    r = db.books.update_one({"book_id": "B900"}, {"$set": {"status": "lent_out"}})
    print("UPDATE: B900 status -> lent_out, modified:", r.modified_count)
    r = db.lending_requests.update_one({"request_id": "R900"}, {"$set": {"status": "accepted"}})
    print("UPDATE: R900 status -> accepted, modified:", r.modified_count)
    print("-" * 50)

    # ---------- DELETE ----------
    r = db.lending_records.delete_one({"record_id": "L900"})
    print("DELETE: removed", r.deleted_count, "completed lending record (L900)")
finally:
    cleanup()
    print("CLEANUP: demo documents removed; real data untouched")
print("-" * 50)
print("All CRUD operations completed.")
