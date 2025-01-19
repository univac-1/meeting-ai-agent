from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# CORSを有効化
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello_world():
    return 'Hello Cloud Run!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
