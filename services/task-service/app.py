from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
import time

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'task_service_requests_total',
    'Total requests to task service',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'task_service_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

TASKS_TOTAL = Counter(
    'task_service_tasks_total',
    'Total number of tasks created'
)

tasks = []

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

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    tasks.append(data)
    TASKS_TOTAL.inc()
    return jsonify({"message": "Task added", "task": data}), 201

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "task", "total_tasks": len(tasks)}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
