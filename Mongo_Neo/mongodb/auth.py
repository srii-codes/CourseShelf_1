import bcrypt
from config import get_db

db = get_db()
MIN_LEN, MAX_LEN = 8, 72  # bcrypt only uses the first 72 bytes


def signup(student_id, password, contact):
    """Register a password for an existing student.
    `contact` (the email on the student record) must match, so strangers
    can't claim someone else's student ID."""
    s = db.students.find_one({"student_id": student_id})
    if not s:
        return "No such student"
    if s.get("password_hash"):
        return "Already registered"
    if (contact or "").strip().lower() != s["contact"].lower():
        return "Contact email does not match our records"
    if not (MIN_LEN <= len(password.encode()) <= MAX_LEN):
        return f"Password must be {MIN_LEN}-{MAX_LEN} bytes long"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db.students.update_one({"student_id": student_id},
                           {"$set": {"password_hash": hashed}})
    return "Signed up"


def login(student_id, password):
    s = db.students.find_one({"student_id": student_id})
    if not s or not s.get("password_hash"):
        return False
    return bcrypt.checkpw(password.encode()[:MAX_LEN], s["password_hash"].encode())


if __name__ == "__main__":
    s = db.students.find_one({"student_id": "S001"})
    print(signup("S001", "test1234", s["contact"]))
    print("Right password:", login("S001", "test1234"))
    print("Wrong password:", login("S001", "wrong"))
