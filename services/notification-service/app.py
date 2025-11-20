from flask import Flask, jsonify, request

app = Flask(__name__)

# Store notifications in memory
notifications = []

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
