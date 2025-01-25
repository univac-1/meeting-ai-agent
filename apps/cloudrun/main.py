from flask import Flask
from flask_cors import CORS

from meeting import create_meeting

app = Flask(__name__)

# CORSを有効化
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello_world():
    return 'Hello Cloud Run!'

@app.route('/meeting', methods=["GET", "POST"])
def meeting():
    return create_meeting()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
