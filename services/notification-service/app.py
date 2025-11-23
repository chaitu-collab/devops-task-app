from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
import time

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'notification_service_requests_total',
    'Total requests to notification service',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'notification_service_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

NOTIFICATIONS_SENT = Counter(
    'notification_service_notifications_sent_total',
    'Total notifications sent'
)

# Store notifications in memory
notifications = []

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

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.get_json()
    message = data.get('message', 'No message')
    user = data.get('user', 'Unknown')

    notification = {
        "id": len(notifications) + 1,
        "user": user,
        "message": message
    }
    notifications.append(notification)
    NOTIFICATIONS_SENT.inc()

    return jsonify({
        "status": "Notification sent",
        "notification": notification
    }), 200

@app.route('/notifications', methods=['GET'])
def get_notifications():
    return jsonify({
        "total": len(notifications),
        "notifications": notifications
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "notification",
        "total_notifications": len(notifications)
    }), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
