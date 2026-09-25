from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # reads MONGO_URI from the .env file in this folder

client = MongoClient(os.environ["MONGO_URI"])
db = client["courseshelf"]

# Index on title (since course_code was removed)
idx1 = db.books.create_index("title")
print("Created index on books.title:", idx1)

# Index on student_id
idx2 = db.students.create_index("student_id")
print("Created index on students.student_id:", idx2)

client.close()