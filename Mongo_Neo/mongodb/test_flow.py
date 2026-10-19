"""
End-to-end test of db_functions on a THROWAWAY database (courseshelf_test),
which is created from the JSON files and dropped at the end.
Your real 'courseshelf' data is never touched.   Run: python test_flow.py
"""
import json
import os

os.environ["DB_NAME"] = "courseshelf_test"   # must be set before importing db_functions

import db_functions as f            # noqa: E402
from config import get_db           # noqa: E402

db = f.db
assert db.name == "courseshelf_test", "refusing to run on a non-test database"

# --- build the test database from the JSON files
for coll in ["students", "books", "lending_requests", "lending_records"]:
    db[coll].delete_many({})
    with open(f"{coll}.json") as fh:
        db[coll].insert_many(json.load(fh))
db.counters.delete_many({})


def expect_error(fn, *a):
    try:
        fn(*a)
    except f.CourseShelfError as e:
        return str(e)
    raise AssertionError(f"{fn.__name__}{a} should have failed")


try:
    book = db.books.find_one({"status": "available"})
    owner = book["owner_id"]
    requester = db.students.find_one({"student_id": {"$ne": owner}})["student_id"]
    third = db.students.find_one({"student_id": {"$nin": [owner, requester]}})["student_id"]

    print("Search:", [b["book_id"] for b in f.search_books(book["title"].split()[0])][:3])
    assert f.search_books("(") == []  # regex characters are treated as plain text

    print("Own book  ->", expect_error(f.create_request, book["book_id"], owner))
    req = f.create_request(book["book_id"], requester)
    print("Request   ->", req)
    print("Duplicate ->", expect_error(f.create_request, book["book_id"], requester))
    req2 = f.create_request(book["book_id"], third)

    print("Wrong owner accept ->", expect_error(f.accept_request, req["request_id"], requester))
    rec = f.accept_request(req["request_id"], owner)
    print("Accepted  ->", rec)
    assert rec["lender_id"] == owner and rec["borrower_id"] == requester
    assert db.books.find_one({"book_id": book["book_id"]})["status"] == "lent_out"
    assert db.lending_requests.find_one({"request_id": req2["request_id"]})["status"] == "declined"
    print("Second accept ->", expect_error(f.accept_request, req["request_id"], owner))
    print("Request lent-out book ->", expect_error(f.create_request, book["book_id"], third))

    print("Wrong owner return ->", expect_error(f.return_book, book["book_id"], requester))
    print("Return    ->", f.return_book(book["book_id"], owner)["returned_on"])
    assert db.books.find_one({"book_id": book["book_id"]})["status"] == "available"
    print("Return again ->", expect_error(f.return_book, book["book_id"], owner))

    new = f.add_book(owner, "Test Book", "1st", "Good")
    print("New book  ->", new["book_id"])
    print("Bad condition ->", expect_error(f.add_book, owner, "X", "1st", "Broken"))
    print("Overdue now:", len(f.overdue_records()))
    print("\nALL CHECKS PASSED")
finally:
    get_db("courseshelf_test").client.drop_database("courseshelf_test")
    print("Test database dropped.")
