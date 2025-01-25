import uuid
from flask import jsonify

def create_meeting():
    # UUIDの生成
    meeting_id = str(uuid.uuid4())

    # TODO:DB保存

    return meeting_id
