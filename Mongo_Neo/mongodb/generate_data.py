from faker import Faker
import json
import random

fake = Faker()

# Students
students = []
courses_pool = ["CSE301", "CSE302", "CSE303", "ECE301", "ECE302", "IT301"]
for i in range(1, 51):
    students.append({
        "student_id": f"S{i:03d}",
        "name": fake.name(),
        "department": random.choice(["CSE", "ECE", "IT"]),
        "courses_enrolled": random.sample(courses_pool, k=random.randint(2, 3)),
        "contact": fake.email()
    })

# Books
titles = ["Database Management Systems", "Operating System Concepts", "Computer Networks",
          "Object Oriented Programming", "Data Structures", "Compiler Design", "Discrete Mathematics"]
editions = ["2nd", "3rd", "4th", "5th"]
books = []
for i in range(1, 51):
    books.append({
        "book_id": f"B{i:03d}",
        "title": random.choice(titles),
        "edition": random.choice(editions),
        "condition": random.choice(["Good", "Fair", "Excellent", "Worn"]),
        "owner_id": f"S{random.randint(1,50):03d}",
        "status": random.choice(["available", "lent_out"])
    })

# Lending Requests
requests = []
for i in range(1, 36):
    requests.append({
        "request_id": f"R{i:03d}",
        "book_id": f"B{random.randint(1,50):03d}",
        "requester_id": f"S{random.randint(1,50):03d}",
        "status": random.choice(["pending", "accepted", "declined"]),
        "requested_on": fake.date_between(start_date="-60d", end_date="today").isoformat()
    })

# Lending Records
records = []
for i in range(1, 36):
    borrowed = fake.date_between(start_date="-90d", end_date="-15d")
    due = fake.date_between(start_date=borrowed, end_date="+15d")
    returned = random.choice([None, fake.date_between(start_date=borrowed, end_date=due).isoformat()])
    records.append({
        "record_id": f"L{i:03d}",
        "book_id": f"B{random.randint(1,50):03d}",
        "lender_id": f"S{random.randint(1,50):03d}",
        "borrower_id": f"S{random.randint(1,50):03d}",
        "borrowed_on": borrowed.isoformat(),
        "due_date": due.isoformat(),
        "returned_on": returned
    })

# Save each as its own JSON file
with open("students.json", "w") as f: json.dump(students, f, indent=2)
with open("books.json", "w") as f: json.dump(books, f, indent=2)
with open("lending_requests.json", "w") as f: json.dump(requests, f, indent=2)
with open("lending_records.json", "w") as f: json.dump(records, f, indent=2)

print("Done! 4 files created.")