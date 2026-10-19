"""
CourseShelf data-access layer (MongoDB). The front end should call ONLY these functions.

Conventions
  * Success  -> returns a dict (or list of dicts) without Mongo's _id.
  * Failure  -> raises CourseShelfError with a human-readable message
                (catch it in the API and show e.message).
  * Anything that changes a book/request takes the id of the student doing it
    (owner_id), and the function checks that student is allowed to do it.
"""
import re
from datetime import date, timedelta
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from config import get_db, LOAN_DAYS, today_str

db = get_db()

VALID_CONDITIONS = ["Good", "Fair", "Excellent", "Worn"]


class CourseShelfError(Exception):
    """Business-rule problem (bad id, not allowed, book unavailable, ...)."""


# ---------------------------------------------------------------- helpers
def _next_id(collection, field, prefix):
    """Atomic ID generator (B001, R036, ...) backed by a 'counters' collection."""
    if db.counters.find_one({"_id": collection}) is None:
        highest = max((int(d[field][len(prefix):]) for d in db[collection].find({}, {field: 1})),
                      default=0)
        try:
            db.counters.insert_one({"_id": collection, "seq": highest})
        except DuplicateKeyError:
            pass  # someone else initialised it first
    doc = db.counters.find_one_and_update({"_id": collection}, {"$inc": {"seq": 1}},
                                          return_document=ReturnDocument.AFTER)
    return f"{prefix}{doc['seq']:03d}"


def _require_student(student_id):
    s = db.students.find_one({"student_id": student_id}, {"_id": 0, "password_hash": 0})
    if not s:
        raise CourseShelfError(f"Student {student_id} not found")
    return s


def _require_book(book_id):
    b = db.books.find_one({"book_id": book_id}, {"_id": 0})
    if not b:
        raise CourseShelfError(f"Book {book_id} not found")
    return b


# ---------------------------------------------------------------- reads
def get_student(student_id):
    return _require_student(student_id)


def get_book(book_id):
    return _require_book(book_id)


def search_books(title="", only_available=False):
    """Case-insensitive 'contains' search. Empty title returns all books."""
    query = {"title": {"$regex": re.escape(title.strip()), "$options": "i"}}
    if only_available:
        query["status"] = "available"
    return list(db.books.find(query, {"_id": 0}))


def my_books(student_id):
    return list(db.books.find({"owner_id": student_id}, {"_id": 0}))


def my_requests(student_id):
    """Requests this student has made."""
    return list(db.lending_requests.find({"requester_id": student_id}, {"_id": 0}))


def incoming_requests(owner_id):
    """Pending requests for books this student owns."""
    ids = [b["book_id"] for b in db.books.find({"owner_id": owner_id}, {"book_id": 1})]
    return list(db.lending_requests.find(
        {"book_id": {"$in": ids}, "status": "pending"}, {"_id": 0}))


def my_borrowed(student_id, active_only=True):
    q = {"borrower_id": student_id}
    if active_only:
        q["returned_on"] = None
    return list(db.lending_records.find(q, {"_id": 0}))


def my_lent(owner_id, active_only=True):
    q = {"lender_id": owner_id}
    if active_only:
        q["returned_on"] = None
    return list(db.lending_records.find(q, {"_id": 0}))


def overdue_records(student_id=None):
    """Active loans whose due_date has passed (optionally only for one borrower)."""
    q = {"returned_on": None, "due_date": {"$lt": today_str()}}
    if student_id:
        q["borrower_id"] = student_id
    return list(db.lending_records.find(q, {"_id": 0}))


# ---------------------------------------------------------------- writes
def add_book(owner_id, title, edition, condition):
    _require_student(owner_id)
    title, edition = (title or "").strip(), (edition or "").strip()
    if not title or not edition:
        raise CourseShelfError("Title and edition are required")
    if condition not in VALID_CONDITIONS:
        raise CourseShelfError(f"Condition must be one of {VALID_CONDITIONS}")
    book = {"book_id": _next_id("books", "book_id", "B"), "title": title,
            "edition": edition, "condition": condition,
            "owner_id": owner_id, "status": "available"}
    db.books.insert_one(dict(book))
    return book


def create_request(book_id, requester_id):
    book = _require_book(book_id)
    _require_student(requester_id)
    if book["owner_id"] == requester_id:
        raise CourseShelfError("You cannot request your own book")
    if book["status"] != "available":
        raise CourseShelfError("Book is currently lent out")
    if db.lending_requests.find_one({"book_id": book_id, "requester_id": requester_id,
                                     "status": "pending"}):
        raise CourseShelfError("You already have a pending request for this book")
    req = {"request_id": _next_id("lending_requests", "request_id", "R"),
           "book_id": book_id, "requester_id": requester_id,
           "status": "pending", "requested_on": today_str()}
    db.lending_requests.insert_one(dict(req))
    return req


def accept_request(request_id, owner_id, days=LOAN_DAYS):
    """Owner accepts a request: creates the loan, marks book lent_out, declines rivals."""
    req = db.lending_requests.find_one({"request_id": request_id})
    if not req:
        raise CourseShelfError("Request not found")
    book = _require_book(req["book_id"])
    if book["owner_id"] != owner_id:
        raise CourseShelfError("Only the book's owner can accept this request")

    # Atomically claim the request (prevents double-accept)...
    claimed = db.lending_requests.find_one_and_update(
        {"request_id": request_id, "status": "pending"}, {"$set": {"status": "accepted"}})
    if not claimed:
        raise CourseShelfError("Request is not pending")
    # ...and atomically claim the book (prevents lending it twice).
    got_book = db.books.update_one({"book_id": book["book_id"], "status": "available"},
                                   {"$set": {"status": "lent_out"}})
    if got_book.modified_count == 0:
        db.lending_requests.update_one({"request_id": request_id}, {"$set": {"status": "pending"}})
        raise CourseShelfError("Book is already lent out")

    today = date.today()
    record = {"record_id": _next_id("lending_records", "record_id", "L"),
              "request_id": request_id, "book_id": book["book_id"],
              "lender_id": book["owner_id"], "borrower_id": req["requester_id"],
              "borrowed_on": today.isoformat(),
              "due_date": (today + timedelta(days=days)).isoformat(),
              "returned_on": None}
    try:
        db.lending_records.insert_one(dict(record))
    except Exception:
        # roll back so data stays consistent
        db.books.update_one({"book_id": book["book_id"]}, {"$set": {"status": "available"}})
        db.lending_requests.update_one({"request_id": request_id}, {"$set": {"status": "pending"}})
        raise

    # other people waiting for this copy can no longer get it
    db.lending_requests.update_many(
        {"book_id": book["book_id"], "status": "pending"}, {"$set": {"status": "declined"}})
    return record


def decline_request(request_id, owner_id):
    req = db.lending_requests.find_one({"request_id": request_id})
    if not req:
        raise CourseShelfError("Request not found")
    if _require_book(req["book_id"])["owner_id"] != owner_id:
        raise CourseShelfError("Only the book's owner can decline this request")
    res = db.lending_requests.update_one({"request_id": request_id, "status": "pending"},
                                         {"$set": {"status": "declined"}})
    if res.modified_count == 0:
        raise CourseShelfError("Request is not pending")
    return {"request_id": request_id, "status": "declined"}


def return_book(book_id, owner_id):
    """Owner confirms the book came back."""
    book = _require_book(book_id)
    if book["owner_id"] != owner_id:
        raise CourseShelfError("Only the book's owner can mark it returned")
    rec = db.lending_records.find_one_and_update(
        {"book_id": book_id, "returned_on": None},
        {"$set": {"returned_on": today_str()}},
        return_document=ReturnDocument.AFTER)
    if not rec:
        raise CourseShelfError("No active loan for this book")
    rec.pop("_id", None)
    db.books.update_one({"book_id": book_id}, {"$set": {"status": "available"}})
    return rec
