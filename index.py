from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re

app = Flask(__name__)
CORS(app)

def load_products():
    with open('books.json', 'r') as file:
        return json.load(file)

products = load_products()

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify({"success": True, "data": products})

@app.route('/api/product', methods=['GET'])
def get_product():
    product_id = request.headers.get('X-Product-ID')  # Get product ID from headers
    if product_id is None:
        return jsonify({"success": False, "message": "Product ID not provided"}), 400

    # Find the product by ID
    product = next((item for item in products if item["id"] == int(product_id)), None)
    
    if product:
        return jsonify({"success": True, "data": product})
    
    return jsonify({"success": False, "message": "Product not found"}), 404

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()

    # Define regex patterns for different queries
    author_pattern = re.compile(r'(show\s+)?books\s+(written\s+by|by|from)\s+(.*)', re.IGNORECASE)
    language_pattern = re.compile(r'(show\s+)?books\s+(in|written\s+in)\s+(.*)', re.IGNORECASE)
    title_pattern = re.compile(r'(show\s+)?book\s+titled\s+(.*)', re.IGNORECASE)
    year_pattern = re.compile(r'(show\s+)?books\s+(published\s+in|from)\s+(\d{4})', re.IGNORECASE)
    
    # Check for specific search patterns in the user message
    if author_match := author_pattern.search(user_message):
        author_name = author_match.group(3).strip()
        filtered_products = [product for product in products if author_name in product["author"].lower()]
        if filtered_products:
            return jsonify({"success": True, "data": filtered_products})
        else:
            return jsonify({"success": True, "reply": f"No books found by {author_name}."})

    elif language_match := language_pattern.search(user_message):
        language = language_match.group(3).strip()
        filtered_products = [product for product in products if language in product["language"].lower()]
        if filtered_products:
            return jsonify({"success": True, "data": filtered_products})
        else:
            return jsonify({"success": True, "reply": f"No books found in {language}."})

    elif title_match := title_pattern.search(user_message):
        title = title_match.group(2).strip()
        filtered_products = [product for product in products if title in product["title"].lower()]
        if filtered_products:
            return jsonify({"success": True, "data": filtered_products})
        else:
            return jsonify({"success": True, "reply": f"No book found titled '{title}'."})

    elif year_match := year_pattern.search(user_message):
        year = year_match.group(3).strip()
        filtered_products = [product for product in products if str(year) in product.get("year", "").lower()]
        if filtered_products:
            return jsonify({"success": True, "data": filtered_products})
        else:
            return jsonify({"success": True, "reply": f"No books found published in {year}."})

    # Default response for unrecognized queries
    else:
        return jsonify({
            "success": True,
            "reply": (
                "I didn't understand that. You can ask me:\n"
                "- Show books written by [Author Name]\n"
                "- Show books written in [Language]\n"
                "- Show book titled [Book Title]\n"
                "- Show books published in [Year]"
            )
        })
if __name__ == '__main__':
    app.run(debug=True)
