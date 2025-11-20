from flask import Flask, jsonify, request

app = Flask(__name__)

# Simple user store (in production, use database)
users = {"admin": "password123", "user": "pass456"}

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username] == password:
        return jsonify({
            "message": "Login successful", 
            "token": f"fake-jwt-token-{username}",
            "username": username
        }), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/auth/verify', methods=['POST'])
def verify():
    data = request.get_json()
    token = data.get('token')
    
    if token and token.startswith('fake-jwt-token'):
        return jsonify({"valid": True, "message": "Token is valid"}), 200
    return jsonify({"valid": False, "message": "Invalid token"}), 401

@app.route('/auth/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "auth"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
