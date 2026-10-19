from pymongo.errors import OperationFailure
from config import get_db

db = get_db()


def ensure(coll, keys, **opts):
    """Create an index; if an old one with the same name but different options exists, replace it."""
    try:
        print(coll.name, "->", coll.create_index(keys, **opts))
    except OperationFailure:
        name = opts.get("name") or "_".join(f"{k}_{d}" for k, d in
                                            (keys if isinstance(keys, list) else [(keys, 1)]))
        coll.drop_index(name)
        print(coll.name, "(rebuilt) ->", coll.create_index(keys, **opts))


# students
ensure(db.students, "student_id", unique=True)

# books
ensure(db.books, "book_id", unique=True)
ensure(db.books, "title")
ensure(db.books, "owner_id")
ensure(db.books, "status")

# lending_requests
ensure(db.lending_requests, "request_id", unique=True)
ensure(db.lending_requests, "book_id")
ensure(db.lending_requests, "requester_id")
ensure(db.lending_requests, "status")

# lending_records
try:  # superseded by the compound index below
    db.lending_records.drop_index("book_id_1")
except OperationFailure:
    pass
ensure(db.lending_records, "record_id", unique=True)
ensure(db.lending_records, [("book_id", 1), ("returned_on", 1)])
ensure(db.lending_records, "borrower_id")
ensure(db.lending_records, "lender_id")
# Database-level guarantee: a book can have at most ONE active (unreturned) loan.
ensure(db.lending_records, "book_id", unique=True, name="one_active_loan_per_book",
       partialFilterExpression={"returned_on": {"$type": "null"}})
