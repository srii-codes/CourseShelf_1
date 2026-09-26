import os
import certifi
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app) # Allows the React frontend to make requests to this backend

# --- Database Connections ---
# MongoDB Setup
mongo_client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
mongo_db = mongo_client["courseshelf"] 
books_collection = mongo_db["books"]

# Neo4j Setup

neo4j_driver = GraphDatabase.driver(
    "neo4j+s://<neo4j username here>.databases.neo4j.io", 
    auth=("<neo4j username here>", "<neo4j password here>")
)

@app.route('/api/search', methods=['GET'])
def search_book():
    query = request.args.get('q', '')
    
    # 1. Query MongoDB for ALL matching books using find()
    mongo_books = list(books_collection.find({"title": {"$regex": query, "$options": "i"}}))
    
    if not mongo_books:
        return jsonify({"message": "Book not found"}), 404

    all_results = []
    
    # 2. Open a single Neo4j session and loop through every found book
    with neo4j_driver.session() as session:
        for mongo_book in mongo_books:
            book_id = mongo_book.get("book_id")
            
            # The actual Cypher query defined
            cypher_query = """
            MATCH (b:Book {book_id: $book_id})-[:LENT_TO*]->(s:Student)
            RETURN s.name
            """
            
            result = session.run(cypher_query, book_id=book_id)
            neo4j_data = [record.values()[0] for record in result] 

            # 3. Append each book's combined data to the list
            all_results.append({
                "book_info": {
                    "title": mongo_book.get("title"),
                    "edition": mongo_book.get("edition", "Unknown"), 
                    "condition": mongo_book.get("condition", "Unknown"),
                    "status": mongo_book.get("status")
                },
                "lending_chain": neo4j_data
            })

    # Return the full list of books instead of just one
    return jsonify(all_results)
if __name__ == '__main__':
    app.run(debug=True, port=5000)
