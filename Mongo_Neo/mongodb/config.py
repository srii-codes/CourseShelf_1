"""Shared settings. Every script gets its DB connection and date format from here."""
import os
from datetime import date
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()  # reads MONGO_URI (and optional DB_NAME) from the .env file

DB_NAME = os.getenv("DB_NAME", "courseshelf")
LOAN_DAYS = int(os.getenv("LOAN_DAYS", "14"))

_client = None


def get_db(name=None):
    """Return a database handle (one shared MongoClient per process)."""
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise RuntimeError("MONGO_URI is not set. Copy .env.example to .env and fill it in.")
        _client = MongoClient(uri)
    return _client[name or os.getenv("DB_NAME", DB_NAME)]


def today_str():
    """Single date convention for the whole project: local date, ISO 'YYYY-MM-DD'."""
    return date.today().isoformat()
