import uuid
from flask import jsonify
import requests
from config import AGORA_APP_ID, AGORA_APP_CERTIFICATE, AGORA_URL

def create_meeting():
    # UUIDの生成
    meeting_id = str(uuid.uuid4())
    
    # Agora APIを呼び出して会議を作成
    # response = requests.post(AGORA_URL, json={
    #     "cname": meeting_id,
    #     "uid": "YOUR_USER_ID",
    #     "clientRequest": {
    #         "token": "YOUR_TOKEN",
    #         "recordingConfig": {
    #             "maxIdleTime": 120,
    #             "streamTypes": 2,
    #             "channels": 1,
    #             "transcodingConfig": {
    #                 "height": 640,
    #                 "width": 480,
    #                 "fps": 15,
    #                 "bitrate": 400,
    #                 "maxResolution": "640x480",
    #                 "minResolution": "640x480"
    #             }
    #         }
    #     }
    # })

    return jsonify({"meeting_id": meeting_id}), 200
