from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
import time

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'auth_service_requests_total',
    'Total requests to auth service',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'auth_service_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

LOGIN_ATTEMPTS = Counter(
    'auth_service_login_attempts_total',
    'Total login attempts',
    ['status']
)

# Simple user store (in production, use database)
users = {"admin": "password123", "user": "pass456"}

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.path
        ).observe(duration)
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
    
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username] == password:
        LOGIN_ATTEMPTS.labels(status='success').inc()
        return jsonify({
            "message": "Login successful",
            "token": f"fake-jwt-token-{username}",
            "username": username
        }), 200
    
    LOGIN_ATTEMPTS.labels(status='failure').inc()
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
