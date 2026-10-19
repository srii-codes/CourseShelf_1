# CourseShelf – MongoDB part

## Setup
1. `pip install -r requirements.txt` (add `requirements-dev.txt` only if you want to regenerate data with `generate_data.py`)
2. Copy `.env.example` to `.env`, fill in `MONGO_URI` (never commit `.env`).
3. `python seed_mongo.py` (loads the JSON data, clears old data)
4. `python indexes.py`
5. Optional: `python aggregations.py`, `python crud.py`, `python test_flow.py` (uses a temporary test DB)

## For the front-end person
Import `db_functions` only. Errors are raised as `db_functions.CourseShelfError` (use `str(e)` as the message).

| Function | Returns |
|---|---|
| `search_books(title="", only_available=False)` | list of books |
| `get_book(book_id)` / `get_student(student_id)` | dict |
| `my_books(student_id)` | books they own |
| `my_requests(student_id)` | requests they made |
| `incoming_requests(owner_id)` | pending requests for their books |
| `my_borrowed(student_id, active_only=True)` / `my_lent(owner_id, active_only=True)` | loan records |
| `overdue_records(student_id=None)` | overdue active loans |
| `add_book(owner_id, title, edition, condition)` | new book (condition: Good/Fair/Excellent/Worn) |
| `create_request(book_id, requester_id)` | new request |
| `accept_request(request_id, owner_id)` | loan record (also declines other pending requests for that book) |
| `decline_request(request_id, owner_id)` | `{request_id, status}` |
| `return_book(book_id, owner_id)` | updated loan record |

`auth.signup(student_id, password, contact)` (contact must match the student's email) and `auth.login(student_id, password)` -> bool.
Pass the logged-in student's id as `owner_id`/`requester_id`; the layer checks ownership but the API must make sure the user is who they claim to be.

## Data model
students(student_id, name, department, courses_enrolled, contact, password_hash?)
books(book_id, title, edition, condition, owner_id, status: available|lent_out)
lending_requests(request_id, book_id, requester_id, status: pending|accepted|declined, requested_on)
lending_records(record_id, request_id, book_id, lender_id, borrower_id, borrowed_on, due_date, returned_on|null)
Dates are ISO strings `YYYY-MM-DD`. Neo4j can be built from the same JSON files.


## Security
Never commit `.env` (it holds `MONGO_URI`). Only `.env.example` with placeholders is tracked. If a credential was ever committed, rotate it.
