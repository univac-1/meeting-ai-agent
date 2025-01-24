from flask import Flask, request, jsonify
from agent.conversation import handle_conversation

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
    
    if not isinstance(messages, list):
        return jsonify({'error': 'messages must be an array'}), 400
    
    responses = []
    for message in messages:
        response = handle_conversation(message)
        responses.extend(response)
    
    return jsonify({'responses': responses})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
