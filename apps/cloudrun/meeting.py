import uuid
from flask import jsonify

def create_meeting():
    # UUIDの生成
    meeting_id = str(uuid.uuid4())

    # TODO:DB保存

    return jsonify({"data":{"meeting_id": meeting_id}}), 200
