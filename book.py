from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from flask_basicauth import BasicAuth
from dotenv import load_dotenv
import os
 
load_dotenv()
 
# เชื่อมต่อกับ MongoDB Atlas
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
 
# เลือก Database และ Collection
db = client["bookstore"]
books_collection = db["books"]
 
app = Flask(__name__)
CORS(app)
 
app.config['BASIC_AUTH_USERNAME'] = 'lucky18'   # ตั้งค่า Username
app.config['BASIC_AUTH_PASSWORD'] = 'iwishyouluck'  # ตั้งค่า Password
 
basic_auth = BasicAuth(app)
 
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
 
# Create (POST)
@app.route('/books', methods=['POST'])
@basic_auth.required
def create_book():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
       
        new_book = {
            "title": data.get("title", ""),
            "author": data.get("author", ""),
            "image_url": data.get("image_url", "")
        }
 
        # record on MongoDB
        result = books_collection.insert_one(new_book)
        new_book["_id"] = str(result.inserted_id)  # convert ObjectId to string
 
        return jsonify(new_book), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
# Read (GET)
@app.route('/books', methods=['GET'])
@basic_auth.required
def get_all_books():
    try:
        books = list(books_collection.find({}, {"_id": 0}))
        return jsonify({"books": books})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
# Read (GET)
@app.route('/books/<title>', methods=['GET'])
@basic_auth.required
def get_book(title):
    try:
        book = books_collection.find_one({"title": title}, {"_id": 0})
        if book:
            return jsonify(book)
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
# update (PUT)
@app.route('/books/<title>', methods=['PUT'])
@basic_auth.required
def update_book(title):
    try:
        data = request.get_json()
        result = books_collection.update_one({"title": title}, {"$set": data})
        if result.modified_count > 0:
            return jsonify({"message": "Book updated successfully"})
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
# Delete (DELETE)
@app.route('/books/<title>', methods=['DELETE'])
@basic_auth.required
def delete_book(title):
    try:
        result = books_collection.delete_one({"title": title})
        if result.deleted_count > 0:
            return jsonify({"message": "Book deleted successfully"})
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)