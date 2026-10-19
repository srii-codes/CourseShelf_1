"""
Generates consistent sample data for CourseShelf (students, books,
lending_requests, lending_records) and writes the 4 JSON files.

Consistency rules enforced:
  * lender_id of a loan is always the owner of the book
  * borrower is never the owner
  * a book has at most ONE active (unreturned) loan; loans of a book never overlap
  * book.status == "lent_out"  <=>  the book has an active loan
  * every loan has exactly one matching "accepted" request (same book + borrower)
  * nobody requests their own book; no duplicate pending request (book + requester)
  * no date is in the future
Output is reproducible (fixed seed). Change SEED for a different dataset.
"""
import json
import random
from collections import defaultdict
from datetime import date, timedelta
from faker import Faker

SEED = 42
N_STUDENTS, N_BOOKS = 50, 50
N_ACTIVE_LOANS, N_RETURNED_LOANS = 10, 25
N_PENDING, N_DECLINED = 12, 8

random.seed(SEED)
Faker.seed(SEED)
fake = Faker()
TODAY = date.today()

DEPARTMENTS = ["CSE", "ECE", "IT"]
COURSES = ["CSE301", "CSE302", "CSE303", "ECE301", "ECE302", "IT301"]
TITLES = ["Database Management Systems", "Operating System Concepts", "Computer Networks",
          "Object Oriented Programming", "Data Structures", "Compiler Design", "Discrete Mathematics"]
EDITIONS = ["2nd", "3rd", "4th", "5th"]
CONDITIONS = ["Good", "Fair", "Excellent", "Worn"]

# ---------- Students ----------
students = [{
    "student_id": f"S{i:03d}",
    "name": fake.name(),
    "department": random.choice(DEPARTMENTS),
    "courses_enrolled": random.sample(COURSES, k=random.randint(2, 3)),
    "contact": fake.email(),
} for i in range(1, N_STUDENTS + 1)]
student_ids = [s["student_id"] for s in students]

# ---------- Books ----------
books = [{
    "book_id": f"B{i:03d}",
    "title": random.choice(TITLES),
    "edition": random.choice(EDITIONS),
    "condition": random.choice(CONDITIONS),
    "owner_id": random.choice(student_ids),
    "status": "available",          # corrected below from the active loans
} for i in range(1, N_BOOKS + 1)]
book_by_id = {b["book_id"]: b for b in books}


def other_student(owner_id):
    return random.choice([s for s in student_ids if s != owner_id])


# ---------- Loans ----------
busy = defaultdict(list)  # book_id -> [(start, end)] used to prevent overlaps
loans = []


def overlaps(book_id, start, end):
    return any(not (end < s or start > e) for s, e in busy[book_id])


# 1) returned loans (finished in the past)
attempts = 0
while sum(1 for l in loans if l["returned_on"]) < N_RETURNED_LOANS and attempts < 5000:
    attempts += 1
    book = random.choice(books)
    borrowed = TODAY - timedelta(days=random.randint(10, 120))
    due = borrowed + timedelta(days=random.choice([7, 14, 21, 30]))
    returned = borrowed + timedelta(days=random.randint(1, (due - borrowed).days + 5))
    if returned >= TODAY or overlaps(book["book_id"], borrowed, returned):
        continue
    busy[book["book_id"]].append((borrowed, returned))
    loans.append({"book_id": book["book_id"], "lender_id": book["owner_id"],
                  "borrower_id": other_student(book["owner_id"]),
                  "borrowed_on": borrowed, "due_date": due, "returned_on": returned})

# 2) active loans (one per book, after all earlier loans of that book)
active_books = set()
attempts = 0
while len(active_books) < N_ACTIVE_LOANS and attempts < 5000:
    attempts += 1
    book = random.choice(books)
    if book["book_id"] in active_books:
        continue
    last_end = max((e for _, e in busy[book["book_id"]]), default=None)
    earliest = max(TODAY - timedelta(days=60), (last_end + timedelta(days=1)) if last_end else TODAY - timedelta(days=60))
    latest = TODAY - timedelta(days=1)
    if earliest > latest:
        continue
    borrowed = earliest + timedelta(days=random.randint(0, (latest - earliest).days))
    due = borrowed + timedelta(days=random.choice([7, 14, 21, 30]))
    active_books.add(book["book_id"])
    busy[book["book_id"]].append((borrowed, TODAY))
    loans.append({"book_id": book["book_id"], "lender_id": book["owner_id"],
                  "borrower_id": other_student(book["owner_id"]),
                  "borrowed_on": borrowed, "due_date": due, "returned_on": None})
    book["status"] = "lent_out"

# ---------- Requests ----------
requests = []
for loan in loans:  # every loan came from an accepted request
    loan["_req"] = {"book_id": loan["book_id"], "requester_id": loan["borrower_id"],
                    "status": "accepted",
                    "requested_on": loan["borrowed_on"] - timedelta(days=random.randint(1, 5))}
    requests.append(loan["_req"])

seen_pending = set()
n = 0
while n < N_PENDING:
    book = random.choice(books)
    req = other_student(book["owner_id"])
    if (book["book_id"], req) in seen_pending:
        continue
    seen_pending.add((book["book_id"], req))
    requests.append({"book_id": book["book_id"], "requester_id": req, "status": "pending",
                     "requested_on": TODAY - timedelta(days=random.randint(0, 30))})
    n += 1
for _ in range(N_DECLINED):
    book = random.choice(books)
    requests.append({"book_id": book["book_id"], "requester_id": other_student(book["owner_id"]),
                     "status": "declined",
                     "requested_on": TODAY - timedelta(days=random.randint(1, 60))})

requests.sort(key=lambda r: r["requested_on"])
for i, r in enumerate(requests, 1):
    r["request_id"] = f"R{i:03d}"

loans.sort(key=lambda l: l["borrowed_on"])
records = []
for i, l in enumerate(loans, 1):
    records.append({
        "record_id": f"L{i:03d}",
        "request_id": l["_req"]["request_id"],
        "book_id": l["book_id"],
        "lender_id": l["lender_id"],
        "borrower_id": l["borrower_id"],
        "borrowed_on": l["borrowed_on"].isoformat(),
        "due_date": l["due_date"].isoformat(),
        "returned_on": l["returned_on"].isoformat() if l["returned_on"] else None,
    })

requests_out = [{"request_id": r["request_id"], "book_id": r["book_id"],
                 "requester_id": r["requester_id"], "status": r["status"],
                 "requested_on": r["requested_on"].isoformat()} for r in requests]

for name, data in [("students", students), ("books", books),
                   ("lending_requests", requests_out), ("lending_records", records)]:
    with open(f"{name}.json", "w") as f:
        json.dump(data, f, indent=2)

print(f"Done: {len(students)} students, {len(books)} books, "
      f"{len(requests_out)} requests, {len(records)} loans "
      f"({N_ACTIVE_LOANS} active). Data is consistent.")
