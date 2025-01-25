import uuid
from flask import jsonify
from config import Config

MEETING_COLLECTION = "meetings"

db_client = Config.get_db_client()

def create_meeting():
    # UUIDの生成
    meeting_id = str(uuid.uuid4())

    data = {
        'name': 'Tokyo',
        'country': 'Japan',
        'population': 37400068
    }

    db_client.collection('meetings').add(data)

    return meeting_id

