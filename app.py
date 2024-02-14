from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__)
socketio = SocketIO(app)

# Check if the message history file exists and if not create it
message_history_file = 'message_history.json'
if not os.path.exists(message_history_file):
    with open(message_history_file, 'w') as file:
        json.dump([], file)

# Load initial message history from JSON file
try:
    with open(message_history_file, 'r') as file:
        message_history = json.load(file)
except json.JSONDecodeError:
    message_history = []

# Print message history for debugging
print("Message History:", message_history)

@app.route('/')
def index():
    return render_template('output.html', messages=message_history)

@socketio.on('send_message')
def handle_message():
    try:
        data = request.json
        sender = data['sender']
        message = data['message']
        
        # Append new message to history
        message_history.append({'sender': sender, 'message': message})
        
        # Broadcast new message to all clients
        emit('new_message', {'sender': sender, 'message': message}, broadcast=True)
        
        # Update JSON file with new message
        with open(message_history_file, 'w') as file:
            json.dump(message_history, file)
            
        return jsonify({'success': True}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    socketio.run(app, debug=True)
    